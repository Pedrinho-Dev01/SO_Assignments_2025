import simpy
import random
import statistics

# Constants
SIM_TIME = 160  # hours
MEAN_INTERARRIVAL = 2  # hours
INSPECTION_TIME_MIN = 0.25  # hours (15 minutes)
INSPECTION_TIME_MAX = 1.05  # hours
REPAIR_PROBABILITY = 0.3
REPAIR_TIME_MIN = 2.1  # hours
REPAIR_TIME_MAX = 4.5  # hours
NUM_REPAIR_STATIONS = 2

# Metrics
inspection_wait_times = []
repair_wait_times = []
inspection_queue_lengths = []
repair_queue_lengths = []
inspection_utilization_time = 0.0
repair_busy_time = 0.0
repair_busy_start = [0.0, 0.0]
repair_station_busy = [False, False]

def bus_process(env, name, inspection_station, repair_station):
    global inspection_utilization_time, repair_busy_time
    
    arrival_time = env.now
    
    # ----- Inspection -----
    with inspection_station.request() as request:
        queue_start = env.now
        yield request
        wait = env.now - queue_start
        inspection_wait_times.append(wait)

        service_time = random.uniform(INSPECTION_TIME_MIN, INSPECTION_TIME_MAX)
        inspection_utilization_time += service_time
        yield env.timeout(service_time)

    # ----- Possible Repair -----
    if random.random() < REPAIR_PROBABILITY:
        with repair_station.request() as request:
            queue_start = env.now
            yield request
            wait = env.now - queue_start
            repair_wait_times.append(wait)

            # Find a free station and record busy time
            for i in range(NUM_REPAIR_STATIONS):
                if not repair_station_busy[i]:
                    repair_station_busy[i] = True
                    repair_busy_start[i] = env.now
                    repair_station_index = i
                    break

            service_time = random.uniform(REPAIR_TIME_MIN, REPAIR_TIME_MAX)
            yield env.timeout(service_time)

            # Free the station and record busy time
            if repair_station_busy[repair_station_index]:
                repair_busy_time += env.now - repair_busy_start[repair_station_index]
                repair_station_busy[repair_station_index] = False

def bus_arrival(env, inspection_station, repair_station):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / MEAN_INTERARRIVAL))
        env.process(bus_process(env, f'Bus{i}', inspection_station, repair_station))
        i += 1

def monitor_queues(env, inspection_station, repair_station):
    while True:
        inspection_queue_lengths.append(len(inspection_station.queue))
        repair_queue_lengths.append(len(repair_station.queue))
        yield env.timeout(0.5)  # check every 30 minutes

def format_time(hours_float):
    total_seconds = int(hours_float * 3600)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    random.seed(42)
    env = simpy.Environment()
    inspection_station = simpy.Resource(env, capacity=1)
    repair_station = simpy.Resource(env, capacity=NUM_REPAIR_STATIONS)

    env.process(bus_arrival(env, inspection_station, repair_station))
    env.process(monitor_queues(env, inspection_station, repair_station))

    env.run(until=SIM_TIME)

    # ---- Results ----
    print("Simulation Results (160 hours):")

    avg_inspection_delay = statistics.mean(inspection_wait_times)
    print(f"Average delay in inspection queue: {format_time(avg_inspection_delay)} (hh:mm:ss)")

    if repair_wait_times:
        avg_repair_delay = statistics.mean(repair_wait_times)
        print(f"Average delay in repair queue: {format_time(avg_repair_delay)} (hh:mm:ss)")
    else:
        print("No buses required repair.")

    print(f"Average inspection queue length: {statistics.mean(inspection_queue_lengths):.2f} buses")
    print(f"Average repair queue length: {statistics.mean(repair_queue_lengths):.2f} buses")

    print(f"Utilization of inspection station: {(inspection_utilization_time / SIM_TIME) * 100:.2f}%")
    print(f"Utilization of repair stations (average): {(repair_busy_time / SIM_TIME / NUM_REPAIR_STATIONS) * 100:.2f}%")

if __name__ == '__main__':
    main()
