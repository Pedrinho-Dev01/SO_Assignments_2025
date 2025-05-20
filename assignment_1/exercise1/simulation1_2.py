import simpy
import random
import statistics

# Constants
SIM_TIME = 160  # hours
# MEAN_INTERARRIVAL = 2  # hours
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

def bus_arrival(env, inspection_station, repair_station, mean_interarrival):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / mean_interarrival))
        env.process(bus_process(env, f'Bus{i}', inspection_station, repair_station))
        i += 1

def monitor_queues(env, inspection_station, repair_station):
    while True:
        inspection_queue_lengths.append(len(inspection_station.queue))
        repair_queue_lengths.append(len(repair_station.queue))
        yield env.timeout(0.5)  # check every 30 minutes

def run_simulation(mean_interarrival):
    random.seed(42)
    env = simpy.Environment()
    inspection_station = simpy.Resource(env, capacity=1)
    repair_station = simpy.Resource(env, capacity=NUM_REPAIR_STATIONS)
    
    env.process(bus_arrival(env, inspection_station, repair_station, mean_interarrival))
    env.process(monitor_queues(env, inspection_station, repair_station))
    env.run(until=SIM_TIME)

def format_time(hours_float):
    total_seconds = int(hours_float * 3600)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    global inspection_wait_times, repair_wait_times, inspection_queue_lengths, repair_queue_lengths
    global inspection_utilization_time, repair_busy_time, repair_busy_start, repair_station_busy
    
    
    # ---------------------------------------------Ex 1.2---------------------------------------------
        
    interarrival_results = []
    
    MEAN_INTERARRIVAL = 2.0
    MIN_INTERARRIVAL = 0.5
    step = 0.1
    critical_interarrival = None
    
    while MEAN_INTERARRIVAL > MIN_INTERARRIVAL:
        # Reset metrics for this simulation run

        inspection_wait_times = []
        repair_wait_times = []
        inspection_queue_lengths = []
        repair_queue_lengths = []
        inspection_utilization_time = 0.0
        repair_busy_time = 0.0
        repair_busy_start = [0.0, 0.0]
        repair_station_busy = [False, False]

        run_simulation(MEAN_INTERARRIVAL)
        
        inspection_queue_delay = statistics.mean(inspection_wait_times) if inspection_wait_times else 0
        repair_queue_delay = statistics.mean(repair_wait_times) if repair_wait_times else 0
        
        inspection_queue_length = statistics.mean(inspection_queue_lengths)
        repair_queue_length = statistics.mean(repair_queue_lengths)
        
        utilization_inspection = inspection_utilization_time / SIM_TIME
        utilization_repair = (repair_busy_time / SIM_TIME) / NUM_REPAIR_STATIONS
        
        result = {
            'interarrival': MEAN_INTERARRIVAL,
            'utilization_inspection': utilization_inspection,
            'utilization_repair': utilization_repair,
            'inspection_queue_length': inspection_queue_length,
            'repair_queue_length': repair_queue_length,
            'inspection_queue_delay': inspection_queue_delay,
            'repair_queue_delay': repair_queue_delay
        }
        interarrival_results.append(result)
        
        # ---- Results ----
        print(f"\nMean Interarrival Time: {MEAN_INTERARRIVAL:.2f} hours")
        print(f"Average delay in inspection queue: {format_time(inspection_queue_delay)} (hh:mm:ss)")

        if repair_wait_times:
            print(f"Average delay in repair queue: {format_time(repair_queue_delay)} (hh:mm:ss)")
        else:
            print("No buses required repair.")
        print(f"Average inspection queue length: {inspection_queue_length:.2f} buses")
        print(f"Average repair queue length: {repair_queue_length:.2f} buses")
        print(f"Utilization of inspection station: {utilization_inspection * 100:.2f}%")
        print(f"Utilization of repair stations: {utilization_repair * 100:.2f}%")
    
        if (utilization_inspection > 0.90 
            or utilization_repair > 0.85 
            or inspection_queue_length > 6.0 
            or inspection_queue_delay > 1.0
            or (len(interarrival_results) > 0 and inspection_queue_delay - interarrival_results[-1]['inspection_queue_delay'] > 0.5)):
            critical_interarrival = MEAN_INTERARRIVAL
            break

            
        MEAN_INTERARRIVAL -= step

    # Print the final result
    print("\nSimulation Results for Exercise 1.2 (160 hours):")
    if critical_interarrival:
        # The maximum arrival rate is the inverse of the minimum stable interarrival time
        max_arrival_rate = 1 / critical_interarrival
        print(f"Minimum mean interarrival time that can be handled: {format_time(critical_interarrival)} (hh:mm:ss)")
        print(f"Maximum bus arrival rate: {max_arrival_rate:.2f} buses per hour")
        print(f"Maximum buses per day: {24 * max_arrival_rate:.1f} buses")
    else:
        print("Could not determine a critical interarrival time within the tested range.")

if __name__ == '__main__':
    main()
