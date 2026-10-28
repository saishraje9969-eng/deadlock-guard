def validate(allocation, maximum, available):
    if not allocation or not allocation[0]:
        raise ValueError("Enter at least one process and one resource type.")
    n, m = len(allocation), len(allocation[0])
    def matrix(name, data):
        if len(data) != n or any(len(row) != m for row in data):
            raise ValueError(f"{name} must have {n} rows and {m} columns.")
        out = []
        for row in data:
            try: vals = [int(x) for x in row]
            except (TypeError, ValueError): raise ValueError(f"{name} values must be integers.")
            if any(x < 0 for x in vals): raise ValueError(f"{name} cannot contain negative values.")
            out.append(vals)
        return out
    allocation = matrix("Allocation", allocation)
    maximum = matrix("Maximum", maximum)
    try: available = [int(x) for x in available]
    except (TypeError, ValueError): raise ValueError("Available values must be integers.")
    if len(available) != m or any(x < 0 for x in available):
        raise ValueError(f"Available must contain {m} non-negative integers.")
    for i in range(n):
        for j in range(m):
            if allocation[i][j] > maximum[i][j]:
                raise ValueError(f"Allocation exceeds maximum for P{i}, R{j}.")
    return allocation, maximum, available

def need_matrix(allocation, maximum):
    return [[maximum[i][j] - allocation[i][j] for j in range(len(maximum[i]))]
            for i in range(len(maximum))]

def bankers_safety(allocation, maximum, available):
    allocation, maximum, available = validate(allocation, maximum, available)
    need = need_matrix(allocation, maximum)
    work = available[:]
    finish = [False] * len(allocation)
    sequence = []
    while True:
        found = False
        for i in range(len(allocation)):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                work = [work[j] + allocation[i][j] for j in range(len(work))]
                finish[i] = True
                sequence.append(i)
                found = True
        if not found:
            break
    return {"safe": all(finish), "sequence": sequence,
            "unfinished": [i for i, done in enumerate(finish) if not done],
            "need": need, "final_work": work}

def request_resources(allocation, maximum, available, process, request):
    allocation, maximum, available = validate(allocation, maximum, available)
    n, m = len(allocation), len(available)
    if not 0 <= process < n: raise ValueError("Invalid process.")
    try: request = [int(x) for x in request]
    except (TypeError, ValueError): raise ValueError("Request values must be integers.")
    if len(request) != m or any(x < 0 for x in request):
        raise ValueError(f"Request must contain {m} non-negative integers.")
    need = need_matrix(allocation, maximum)
    if any(request[j] > need[process][j] for j in range(m)):
        return {"granted": False, "reason": "Request exceeds the process's remaining need."}
    if any(request[j] > available[j] for j in range(m)):
        return {"granted": False, "reason": "Insufficient available resources; request must wait."}
    new_alloc = [row[:] for row in allocation]
    new_avail = available[:]
    for j in range(m):
        new_alloc[process][j] += request[j]
        new_avail[j] -= request[j]
    safety = bankers_safety(new_alloc, maximum, new_avail)
    if not safety["safe"]:
        return {"granted": False, "reason": "Request would result in an unsafe state.", "safety": safety}
    return {"granted": True, "reason": "Request granted; resulting state is safe.",
            "allocation": new_alloc, "available": new_avail, "safety": safety}

def detect_deadlock(allocation, request, available):
    if not allocation or not allocation[0]:
        raise ValueError("Enter at least one process and resource type.")
    n, m = len(allocation), len(allocation[0])
    allocation, _, available = validate(allocation, allocation, available)
    if len(request) != n or any(len(row) != m for row in request):
        raise ValueError("Current Request matrix has the wrong dimensions.")
    try: request = [[int(x) for x in row] for row in request]
    except (TypeError, ValueError): raise ValueError("Request values must be integers.")
    if any(x < 0 for row in request for x in row): raise ValueError("Request cannot be negative.")
    work = available[:]
    finish = [all(x == 0 for x in row) for row in allocation]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(m)):
                work = [work[j] + allocation[i][j] for j in range(m)]
                finish[i] = True
                changed = True
    deadlocked = [i for i, done in enumerate(finish) if not done]
    return {"deadlock": bool(deadlocked), "deadlocked_processes": deadlocked,
            "finish": finish, "final_work": work}

def graph_edges(allocation, request):
    edges = []
    for i, row in enumerate(allocation):
        for j, value in enumerate(row):
            if value: edges.append((i, j, "allocation", value))
            if request[i][j]: edges.append((i, j, "request", request[i][j]))
    return edges
