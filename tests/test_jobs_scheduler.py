from collections import defaultdict


def test_jobs_scheduler_basic_flow(client):
    # Test node creation
    node = {"max_concurrent_jobs": 2, "max_total_jobs": 5, "vcpu_units": 5, "memory": 4000}
    post_response = client.post("/api/v1/nodes", json=[node])
    assert post_response.status_code == 201
    assert len(post_response.json()) == 1

    get_response = client.get("/api/v1/nodes")
    assert get_response.status_code == 200
    assert get_response.json() == post_response.json()
    node_id = get_response.json()[0]["id"]

    # Test job schedulement
    job = {"total_run_time": 10000, "vcpu_units": 1, "memory": 1000}  # 10 seconds
    job_response = client.post("/api/v1/jobs", json=[job])
    assert job_response.status_code == 201
    assert len(job_response.json()) == 1
    job_id = job_response.json()[0]["id"]

    nodes_response = client.get("/api/v1/nodes")
    assert nodes_response.status_code == 200
    assert len(nodes_response.json()) == 1
    assert nodes_response.json()[0]["id"] == node_id
    assert len(nodes_response.json()[0]["jobs"]) == len(job_response.json())
    assert nodes_response.json()[0]["jobs"][0]["id"] == job_id

    # Test job schedulement (exceeds available resources)
    job = {"total_run_time": 10000, "vcpu_units": 1, "memory": 10000}  # 10 seconds
    job_response = client.post("/api/v1/jobs", json=[job])
    assert job_response.status_code == 503

    # Test node removal (unsuccessful)
    response = client.delete(f"/api/v1/nodes/{node_id}")
    # impossible to remove node since there is no other node to reschedule jobs on
    assert response.status_code == 503

    # Test job termination
    response = client.delete(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 204

    response = client.get("/api/v1/nodes")
    assert response.status_code == 200
    node = response.json()[0]
    assert node["jobs"][0]["status"] == "terminated"

    # Test node removal (successful)
    response = client.delete(f"/api/v1/nodes/{node_id}")
    assert response.status_code == 204

    response = client.get("/api/v1/nodes")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_jobs_scheduler_complex_flow(client):
    nodes = [
        {"max_concurrent_jobs": 1, "max_total_jobs": 2, "vcpu_units": 50, "memory": 50000},
        {"max_concurrent_jobs": 2, "max_total_jobs": 10, "vcpu_units": 50, "memory": 50000},
    ]
    post_response = client.post("/api/v1/nodes", json=nodes)
    assert post_response.status_code == 201
    assert len(post_response.json()) == 2

    jobs = [
        {"total_run_time": 500000, "vcpu_units": 1, "memory": 1000},  # job 0  # 500 seconds
        {"total_run_time": 300000, "vcpu_units": 1, "memory": 1000},  # job 1  # 300 seconds
        {"total_run_time": 300000, "vcpu_units": 1, "memory": 1000},  # job 2  # 300 seconds
        {"total_run_time": 150000, "vcpu_units": 1, "memory": 1000},  # job 3  # 150 seconds
        {"total_run_time": 150000, "vcpu_units": 1, "memory": 1000},  # job 4  # 150 seconds
        {"total_run_time": 50000, "vcpu_units": 1, "memory": 1000},  # job 5  # 50 seconds
        {"total_run_time": 50000, "vcpu_units": 1, "memory": 1000},  # job 6  # 50 seconds
        {"total_run_time": 100000, "vcpu_units": 1, "memory": 1000},  # job 7  # 100 seconds
        {"total_run_time": 100000, "vcpu_units": 1, "memory": 1000},  # job 8  # 100 seconds
        {"total_run_time": 100000, "vcpu_units": 1, "memory": 1000},  # job 9  # 100 seconds
    ]
    job_response = client.post("/api/v1/jobs", json=jobs)
    assert job_response.status_code == 201
    assert len(job_response.json()) == len(jobs)

    nodes_response = client.get("/api/v1/nodes")
    assert nodes_response.status_code == 200
    assert len(nodes_response.json()) == 2

    node_1 = nodes_response.json()[0]
    node_2 = nodes_response.json()[1]

    # node_1 has 2 jobs: job 1 and job 9
    assert len(node_1["jobs"]) == 2
    # all remaining 8 jobs are split in two threads on node_2
    assert len(node_2["jobs"]) == 8

    # exceed max jobs number possible to run on all nodes
    jobs = [
        {"total_run_time": 300000, "vcpu_units": 1, "memory": 1000},  # job 0  # 300 seconds
        {"total_run_time": 300000, "vcpu_units": 1, "memory": 1000},  # job 1  # 300 seconds
        {"total_run_time": 300000, "vcpu_units": 1, "memory": 1000},  # job 2  # 300 seconds
    ]
    job_response = client.post("/api/v1/jobs", json=jobs)
    assert job_response.status_code == 503

    # terminate jobs from one node to free up some space for the new jobs
    job_ids = [job["id"] for job in node_1["jobs"]]
    for job_id in job_ids:
        response = client.delete(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 204

    # try to submit 3 above declared jobs once again
    job_response = client.post("/api/v1/jobs", json=jobs)
    assert job_response.status_code == 201
    new_jobs = job_response.json()
    jobs_in_node_1 = [job for job in new_jobs if job["node_id"] == node_1["id"]]

    # add new node_3
    nodes = [
        {"max_concurrent_jobs": 1, "max_total_jobs": 5, "vcpu_units": 50, "memory": 50000},
    ]
    post_response = client.post("/api/v1/nodes", json=nodes)
    assert post_response.status_code == 201
    node_3 = post_response.json()[0]

    # remove node_1, so the jobs from node_1 will move to node_3
    response = client.delete(f"/api/v1/nodes/{node_1['id']}")
    assert response.status_code == 204

    get_response = client.get("/api/v1/nodes")
    assert get_response.status_code == 200
    node_3 = [node for node in get_response.json() if node["id"] == node_3["id"]][0]
    assert len(jobs_in_node_1) == len(node_3["jobs"])
    assert jobs_in_node_1[0]["id"] == node_3["jobs"][0]["id"]
