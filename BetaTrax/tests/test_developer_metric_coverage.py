from BetaTrax.developer_metrics import build_effectiveness_metrics


class TestDeveloperMetricCoverage:
	def test_insufficient_data_when_fixed_below_20(self):
		metrics = build_effectiveness_metrics(fixed_count=19, reopened_count=3)

		assert metrics['fixed_count'] == 19
		assert metrics['reopened_count'] == 3
		assert metrics['ratio'] is None
		assert metrics['classification'] == 'Insufficient data'
		assert 'Need at least 20 fixed defects' in metrics['message']

	def test_good_when_ratio_is_less_than_1_over_32(self):
		metrics = build_effectiveness_metrics(fixed_count=20, reopened_count=0)

		assert metrics['classification'] == 'Good'
		assert metrics['ratio'] == 0.0
		assert metrics['message'] is None

	def test_fair_at_1_over_32_boundary(self):
		metrics = build_effectiveness_metrics(fixed_count=32, reopened_count=1)

		assert metrics['classification'] == 'Fair'
		assert metrics['ratio'] == 0.03125

	def test_fair_when_ratio_is_below_1_over_8(self):
		metrics = build_effectiveness_metrics(fixed_count=24, reopened_count=2)

		assert metrics['classification'] == 'Fair'
		assert metrics['ratio'] == 0.083333

	def test_poor_at_1_over_8_boundary(self):
		metrics = build_effectiveness_metrics(fixed_count=24, reopened_count=3)

		assert metrics['classification'] == 'Poor'
		assert metrics['ratio'] == 0.125

	def test_poor_when_ratio_is_above_1_over_8(self):
		metrics = build_effectiveness_metrics(fixed_count=20, reopened_count=5)

		assert metrics['classification'] == 'Poor'
		assert metrics['ratio'] == 0.25
