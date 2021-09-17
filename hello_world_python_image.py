from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    "owner": "TYC",
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="hello_world_python",
    default_args=args,
    schedule_interval="0 0 * * *",
    start_date=datetime(2020, 4, 26),
    catchup=False,
)

start = DummyOperator(task_id="run_this_first", dag=dag)

next = KubernetesPodOperator(
    namespace="airflow",
    image="python:3.8-slim",
    cmds=["sleep", "10"],
    name="task-name",
    task_id="python-pod-test",
    is_delete_operator_pod=True,
    in_cluster=True,
    get_logs=True,
    node_selectors={"cloud.google.com/gke-nodepool": "gpu-node-pool"},
    tolerations=[
        {
            "key": "nvidia.com/gpu",
            "operator": "Equal",
            "value": "present",
            "effect": "NoSchedule",
        }
    ],
    resources={"limit_gpu": 1},
    startup_timeout_seconds=60 * 5,
    dag=dag,
)

next.set_upstream(start)
