# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from reconciliation import reconcile_from_child

# blocked/retried child from your latest run history
CHILD_TASK_ID = "b9bb76d9-4693-42f4-80e0-863d9dbcda4e"

reconcile_from_child(CHILD_TASK_ID)
