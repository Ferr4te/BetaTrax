MIN_FIXED_FOR_METRIC = 20
GOOD_THRESHOLD = 0.03125
FAIR_THRESHOLD = 0.125


def build_effectiveness_metrics(fixed_count, reopened_count):
    """Return effectiveness metrics using sprint-3 conformance thresholds."""
    if fixed_count < MIN_FIXED_FOR_METRIC:
        return {
            'fixed_count': fixed_count,
            'reopened_count': reopened_count,
            'ratio': None,
            'classification': 'Insufficient data',
            'message': (
                f'Developer has fixed {fixed_count} defects. '
                f'Need at least {MIN_FIXED_FOR_METRIC} fixed defects for meaningful metric.'
            ),
        }

    ratio = reopened_count / fixed_count

    if ratio < GOOD_THRESHOLD:
        classification = 'Good'
    elif ratio < FAIR_THRESHOLD:
        classification = 'Fair'
    else:
        classification = 'Poor'

    return {
        'fixed_count': fixed_count,
        'reopened_count': reopened_count,
        'ratio': round(ratio, 6),
        'classification': classification,
        'message': None,
    }
