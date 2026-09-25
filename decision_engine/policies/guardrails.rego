package aexyron.guardrails

import future.keywords.in

default allow = false

# Execution is permitted if blast radius is within limits, paths preserved, and rate limit ok
allow {
    not circuit_breaker_active
    blast_radius_safe
    redundant_paths_preserved
    rate_limit_ok
}

blast_radius_safe {
    input.candidate_action.drained_capacity_ratio <= 0.25
    input.candidate_action.affected_gpu_nodes == 0
}

redundant_paths_preserved {
    input.candidate_action.min_remaining_ecmp_paths >= 1
}

rate_limit_ok {
    input.recent_actions_count_60s < 3
}

circuit_breaker_active {
    data.system_state.circuit_breaker_tripped == true
}
