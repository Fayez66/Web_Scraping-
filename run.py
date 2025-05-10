from multiprocessing import Process
from Scripts import UpWorkScript, FreelancerScript, MostaqelScript, FreelanceYardScript


def run_all():
    procs = [
        Process(target=UpWorkScript.main),
        Process(target=FreelancerScript.main),
        Process(target=MostaqelScript.main),
        Process(target=FreelanceYardScript.main)
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == "__main__":
    run_all()