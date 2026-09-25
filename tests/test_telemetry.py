"""Tests for Layer 1: Streaming Telemetry."""
from telemetry.kafka_topics import InterfaceMetricSample, EBPFDropSample


def test_interface_metric_serialization():
    sample = InterfaceMetricSample(
        device_id="spine-01",
        interface_id="eth1",
        timestamp=1695648000.0,
        octets_rx=1000000,
        octets_tx=1200000,
        packets_rx=10000,
        packets_tx=12000,
        errors_rx=0,
        errors_tx=0,
        drops_rx=5,
        drops_tx=2,
        queue_occupancy_pct=14.5,
        optical_power_dbm=-3.2,
    )
    raw_json = sample.to_json()
    assert "spine-01" in raw_json
    assert "eth1" in raw_json

    restored = InterfaceMetricSample.from_json(raw_json)
    assert restored.device_id == "spine-01"
    assert restored.drops_rx == 5
    assert restored.queue_occupancy_pct == 14.5


def test_ebpf_drop_sample():
    sample = EBPFDropSample(
        host_id="host-01",
        src_ip="10.0.1.10",
        dst_ip="10.0.2.20",
        src_port=5201,
        dst_port=5201,
        protocol="TCP",
        drop_reason="SKB_DROP_REASON_TCP_CSUM",
        tcp_rtt_us=125.4,
        retransmissions=3,
    )
    raw_json = sample.to_json()
    assert "SKB_DROP_REASON_TCP_CSUM" in raw_json
    restored = EBPFDropSample.from_json(raw_json)
    assert restored.host_id == "host-01"
    assert restored.retransmissions == 3
