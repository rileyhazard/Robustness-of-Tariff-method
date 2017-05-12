import pandas as pd
import numpy as np

from src.getters import (
    get_gold_standard,
    get_codebook,
    get_cause_map,
    get_metadata,
    get_smartva_symptoms,
    get_smartva_predictions
)
import src.metrics as perf


def get_endorsements(module, symptoms, gold_standard):
    codebook = get_codebook('{}_symptom.csv'.format(module))

    df = symptoms.groupby(gold_standard).mean()

    # Some symptoms are never endorsed. This may be because of changes in
    # the method or if the shortened questionnaire is used many columns are
    # explicited unused. The prefered format for viewing is columns of causes
    # and rows of symptoms, so the dataframe is transposed.
    df = df.loc[:, df.sum() > 0].T
    col_order = ['description'] + df.columns.tolist()
    df['description'] = df.index.to_series().map(codebook.question)
    row_order = [q for q in codebook.index if q in df.index]
    df = df.loc[row_order, col_order]

    return df


def get_misclassification(gold_standard, prediction):
    df = pd.crosstab(gold_standard, prediction)
    df.index.name = None
    df.columns.name = None

    # Ensure "Undetermined" is the last column to preserve the diagonal
    if 'Undetermined' in df.columns:
        cols = df.columns.tolist()
        cols.remove('Undetermined')
        cols.append('Undetermined')
        df = df.loc[:, cols]

    return df


def get_classification_statistics(gold_standard, prediction):
    causes = gold_standard.unique()
    stats = ['CCC', 'PPV', 'NPV', 'Sensitivity', 'Specificity', 'Accuracy']
    df = []
    for cause in causes:
        params = cause, gold_standard, prediction
        df.append([
            perf.calc_ccc(*params),
            perf.calc_positive_predictive_value(*params),
            perf.calc_negative_predictive_value(*params),
            perf.calc_sensitivity(*params),
            perf.calc_specificity(*params),
            perf.calc_specific_accuracy(*params),
        ])
    df = pd.DataFrame(df, index=causes, columns=stats)
    df = df.sort_index()
    return df


def get_overall_statistics(gold_standard, prediction):
    stats = ['CSMF Accuracy', 'CCCSMF Accuracy', 'Median CCC', 'Mean CCC']
    ccc = [perf.calc_ccc(cause, gold_standard, prediction)
           for cause in np.unique(gold_standard)]
    csmf = perf.calc_csmf_accuracy(gold_standard, prediction)
    return pd.Series([
        csmf,
        perf.correct_csmf_accuracy(csmf),
        np.median(ccc),
        np.mean(ccc),
    ], index=stats)


def get_all_data(path, module, dataset, cause_map, rules):
    va46_text46 = get_cause_map(module, 'smartva', 'smartva_text')
    gold_standard = get_gold_standard(dataset, module)
    gold_standard = gold_standard.gs_text46.replace(cause_map)
    prediction = get_smartva_predictions(path, module, rules, va46_text46)
    prediction = prediction.replace(cause_map)
    symptoms = get_smartva_symptoms(path, module)

    # Unmatched observations are usually occur because the validation data
    # classifies an observation in one module, but SmartVA classifies it into
    # another. This is less than 10 observations per module. Since the wrong
    # set of questions and a cause from the wrong list is used these cause
    # problems and should be dropped.
    matched = gold_standard.index.intersection(symptoms.index)
    gold_standard = gold_standard.loc[matched]
    prediction = prediction.loc[matched]
    symptoms = symptoms.loc[matched]

    endorsements = get_endorsements(module, symptoms, gold_standard)
    misclassification = get_misclassification(gold_standard, prediction)
    stats_by_cause = get_classification_statistics(gold_standard, prediction)
    overall_stats = get_overall_statistics(gold_standard, prediction)

    col_order = ['Module'] + stats_by_cause.columns.tolist()
    stats_by_cause['Module'] = module.title()
    stats_by_cause = stats_by_cause.loc[:, col_order]

    idx_order = ['Module'] + overall_stats.index.tolist()
    overall_stats['Module'] = module.title()
    overall_stats = overall_stats.loc[idx_order]

    return (gold_standard, prediction, endorsements, misclassification,
            stats_by_cause, overall_stats)


def main(path, dataset, outfile=None, cause_list='smartva_reporting',
         rules=True):
    modules = ['adult', 'child', 'neonate']
    data = dict()
    for module in modules:
        if cause_list in ['gs_text34', 'gs_text46', 'smartva_text',
                          'smartva_reporting']:
            cause_map = get_cause_map(module, 'smartva_text', cause_list)
        else:
            # Assume cause_list is a metadata file or set of files
            cause_map = get_metadata(cause_list, module, 'cause_map')
            if not cause_map:
                cause_map = get_cause_map(module, 'smartva_text', cause_list)
        data[module] = get_all_data(path, module, dataset, cause_map, rules)

    stats_by_cause = pd.concat([data[module][4] for module in modules])
    overall_stats = pd.concat([data[module][5] for module in modules], axis=1)

    spurious_associations = get_metadata('src/data/smartva_spurious.yml',
                                         keys='spurious_associations')

    if outfile:
        # Pandas set cell style on header cells which cannot be overwritten
        # by row and column formatting. Reset the Pandas formats before
        # writing headers
        pd.formats.format.header_style = None

        writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
        workbook = writer.book

        pct_fmt = workbook.add_format({'num_format': '0.0%'})
        header_fmt = workbook.add_format({'rotation': 60, 'bold': True})
        bold_fmt = workbook.add_format({'bold': True})
        outlier_fmt = workbook.add_format({'bg_color': '#FF8080'})
        outlier_cond = {
            'type': 'cell',
            'criteria': 'greater than',
            'value': 9,
            'format': outlier_fmt,
        }
        spur_fmt = workbook.add_format({'num_format': '0.0%',
                                        'bg_color': '#A6BDDB'})

        sheet_name = 'Overall Stats'
        overall_stats.T.to_excel(writer, sheet_name=sheet_name, index=False)
        sheet = writer.sheets[sheet_name]
        sheet.set_row(0, None, bold_fmt)
        sheet.autofilter(0, 0, overall_stats.index.shape[0],
                         overall_stats.columns.shape[0])
        sheet.freeze_panes(1, 0)
        sheet.set_column(0, 0, 9.43)    # Module
        sheet.set_column(1, stats_by_cause.columns.shape[0], 11.86, pct_fmt)

        sheet_name = 'Stats by Cause'
        stats_by_cause.to_excel(writer, sheet_name=sheet_name,
                                index_label='Cause')
        sheet = writer.sheets[sheet_name]
        sheet.set_row(0, None, bold_fmt)
        sheet.autofilter(0, 0, stats_by_cause.index.shape[0],
                         stats_by_cause.columns.shape[0])
        sheet.freeze_panes(1, 0)
        sheet.set_column(0, 0, 37.14)   # Cause
        sheet.set_column(1, 1, 9.43)    # Module
        sheet.set_column(2, stats_by_cause.columns.shape[0], 11.86, pct_fmt)

        for module in modules:
            df = data[module][3]
            sheet_name = '{} Misclassification'.format(module.title())
            df.to_excel(writer, sheet_name=sheet_name)
            sheet = writer.sheets[sheet_name]

            last_row, last_col = df.index.shape[0], df.columns.shape[0]
            sheet.autofilter(0, 0, last_row, last_col)
            sheet.freeze_panes(1, 1)
            sheet.set_column(0, 0, 33)   # GS Cause
            sheet.set_column(1, last_col, 4.43)   # Counts
            sheet.set_row(0, None, header_fmt)
            sheet.write(0, 0, 'Gold Standard', bold_fmt)
            sheet.conditional_format(1, 1, last_row, last_col, outlier_cond)

            df = data[module][2]
            sheet_name = '{} Endorsements'.format(module.title())
            df.to_excel(writer, sheet_name=sheet_name)
            sheet = writer.sheets[sheet_name]

            for cause, spurious in spurious_associations[module].items():
                if cause not in df.columns:
                    continue
                cause_index = df.columns.get_loc(cause) + 1
                for spur in spurious:
                    if spur not in df.index:
                        continue
                    symptom_index = df.index.get_loc(spur) + 1
                    val = df.loc[spur, cause]
                    sheet.write(symptom_index, cause_index, val, spur_fmt)

            sheet.autofilter(0, 0, df.index.shape[0], df.columns.shape[0])
            sheet.freeze_panes(1, 2)
            sheet.set_column(0, 0, 10.71)   # Symptom variable
            sheet.set_column(1, 1, 95.71)   # Symptom description
            sheet.set_column(2, df.columns.shape[0], None, pct_fmt)  # Percents
            sheet.set_row(0, None, header_fmt)
            sheet.write(0, 0, 'Predictor', bold_fmt)
            sheet.write(0, 1, 'Description', bold_fmt)

        writer.save()

    return (
        overall_stats,
        stats_by_cause,
        data['adult'][3],
        data['adult'][2],
        data['child'][3],
        data['child'][2],
        data['neonate'][3],
        data['neonate'][2],
    )


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser("Produce an excel file with performance "
                                     "statistic, endorsement rates and "
                                     "misclassification matrices from "
                                     "Smartva output")
    parser.add_argument('input', help='Path to SmartVA output')
    parser.add_argument('output', help='Filename of output xlsx')
    parser.add_argument('-d', '--dataset', default='phmrc',
                        choices=['phmrc', 'nhmrc'],
                        help='Filename of output xlsx')
    parser.add_argument('-c', '--cause-list', default='smartva_reporting',
                        help='Either a column in the cause map or a path to a '
                             'yaml file with a cause mapping dict')
    parser.add_argument('--no-rules', action='store_false', dest='rules')
    args = parser.parse_args()

    if not args.output.endswith('.xlsx'):
        args.output += '.xlsx'
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'external', args.output)
    main(args.input, args.dataset, outfile, args.cause_list, args.rules)
