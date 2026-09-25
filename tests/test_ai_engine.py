"""Tests for Layer 3: AI Anomaly & Prediction Engine."""
from ai_engine.anomaly_detector import FastAnomalyDetector
from ai_engine.failure_predictor import FailurePredictor


def test_fast_anomaly_detector():
    detector = FastAnomalyDetector(contamination=0.05)
    key = "leaf-01:eth1"

    # Push nominal values (0.0% packet drop)
    for _ in range(10):
        detector.ingest_metric(key, 0.001)

    # Ingest sudden anomaly (12% packet drops)
    anomaly_result = detector.ingest_metric(key, 0.12)
    assert anomaly_result is not None
    assert anomaly_result["is_anomaly"] is True
    assert anomaly_result["entity"] == key


def test_failure_predictor_horizon():
    predictor = FailurePredictor(warning_threshold=0.70)
    
    # Degraded laser power and high CRC velocity
    res = predictor.predict_failure_horizon(
        entity_id="transceiver_spine01_port1",
        optical_power_trend_dbm=-2.1,
        crc_error_velocity=24.0,
        buffer_occupancy_growth_rate=12.0,
    )
    assert res is not None
    assert res["impending_failure"] is True
    assert res["horizon_seconds"] >= 20.0
    assert len(res["reasons"]) >= 2
