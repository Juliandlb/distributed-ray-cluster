import ray

ray.init(
    address="auto",
    _temp_dir="/mnt/data/distributed-ray-cluster/ray_cluster/tmp",
)

print("Ray head node started successfully!")
