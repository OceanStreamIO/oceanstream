import time
import psutil


def display_profiling_and_summary_info(profiling_info, config):
    if config["profile"]:
        print("\n--- Profiling Information ---")
        if not profiling_info:
            print("No profiling information available.")
        else:
            # Determine the longest task name for alignment
            longest_task_name = max(len(task) for task in profiling_info)

            # Header
            header = f"{'Task'.ljust(longest_task_name)} | Execution Time (s) | CPU Usage (%) | Memory Usage (MB)"
            print(header)
            print("-" * len(header))

            # Data rows for profiling
            for task, info in profiling_info.items():
                execution_time = info.get("execution_time")
                if execution_time is not None:
                    execution_time_str = f"{execution_time:.2f}"
                else:
                    execution_time_str = "N/A"

                cpu_usage = info.get("cpu_usage", "N/A")
                if cpu_usage != "N/A":
                    cpu_usage = f"{cpu_usage:.2f}"

                memory_usage = info.get("memory_usage")

                if memory_usage is not None:
                    memory_usage_mb = memory_usage / (1024 * 1024)  # Convert bytes to megabytes
                    memory_usage_str = f"{memory_usage_mb:.2f}"
                else:
                    memory_usage_str = "N/A"

                row = f"{task.ljust(longest_task_name)} | {execution_time_str:18} | {cpu_usage:13} | {memory_usage_str:16}"
                print(row)


def start_profiling():
    start_time = time.time()
    start_cpu = psutil.cpu_percent(interval=None)
    start_memory = psutil.virtual_memory().used

    return start_time, start_cpu, start_memory


def end_profiling(start_time, start_cpu, start_memory):
    end_time = time.time()
    end_cpu = psutil.cpu_percent(interval=None)
    end_memory = psutil.virtual_memory().used

    profiling_info = {
        "execution_time": end_time - start_time,
        "cpu_usage": end_cpu - start_cpu,
        "memory_usage": end_memory - start_memory  # In bytes
    }

    return profiling_info
