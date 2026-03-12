# Data Notes

## Selected primary dataset

- Program: Alibaba Cluster Trace Program
- Release: `cluster-trace-v2018`
- Official documentation:
  - <https://github.com/alibaba/clusterdata>
  - <https://raw.githubusercontent.com/alibaba/clusterdata/master/cluster-trace-v2018/trace_2018.md>

## Why this release

- It is directly relevant to cluster resource management.
- It exposes machine-level utilization needed for a first predictive capacity-control loop.
- The metadata file is small and immediately accessible.
- The large utilization file can be downloaded resumably with `curl`.

## Files used in the first pass

- `machine_meta.tar.gz`
- `machine_usage.tar.gz`

## Storage warning

- `machine_usage.tar.gz` is approximately `1.7 GiB` compressed and much larger after extraction.
- The preprocessing script reads the CSV from the tar archive directly and avoids materializing the full extracted file when possible.

## Optional later extensions

- Add `container_usage.tar.gz` if service-level or container-level scaling is required.
- Add `cluster-trace-microservices-v2021` for a stronger microservice autoscaling variant.
