import matplotlib.pyplot as plt
import datetime
import numpy as np
import requests
import re

# https://www.npmjs.com/package/amtrak?activeTab=readme
# Available Endpoints for https://api-v3.amtraker.com/v3/
# /trains
# /trains/:trainId
# /stations
# /stations/:stationId
# /stale

# Object wrapper for dictionary
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return '<%s>' % str('\n '.join('%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.items()))

    def __getattr__( self, attr):
        value = self.__dict__.get(attr)
        if not value:
            print(f'Warning: \'Struct\' object has no attribute \'{attr}\', returning -1')
            return -1
        else:
            return value

class Amtrak:
    def __init__( self):
        self.api = 'https://api-v3.amtraker.com/v3/'

    def fetchAllTrains( self):
        data = requests.get( self.api + 'trains').json()
        return [ Struct(**v[0]) for k, v in data.items()]

    def fetchTrain( self, trainID):
        data = requests.get( self.api + 'trains/' + str(trainID)).json()
        return Struct(**data[str(trainID)][0])

    def fetchAllStations( self):
        data = requests.get( self.api + 'stations').json()
        return [ Struct(**v) for k, v in data.items()]

    def fetchStation( self, stationID):
        data = requests.get( self.api + 'stations/' + stationID).json()
        return Struct(**data[stationID])

    # def fetchLatestTrain( self):
    #     latestTrain = Struct()
    #     latestTime = -1
    #     for train in self.fetchAllTrains():
    #         howLate = float()
    #         txt = train.trainTimely
    #         if 'Late' in train.trainTimely:
    #             match = re.search(r"^(\d*) Hours?, (\d*) Minutes? Late$", txt)
    #             if match:
    #                 howLate = float(match.group(1)) + (float(match.group(2)) / 60)
    #             else:
    #                 match = re.search(r"(\d*) Minutes? Late$", txt)
    #                 if not match:
    #                     print("NO MATCH")
    #                     exit(0)
    #                 else:
    #                     howLate = float(match.group(1)) / 60
    # 
    #             if howLate > latestTime:
    #                 latestTime = howLate
    #                 latestTrain = train
    # 
    #     return latestTrain, latestTrain.trainTimely

    def fetchTrainPerformance( self, plot=False):
        count = 0
        total = 0
        allLateness = []
        latestTime = -1
        latestTrain = Struct()
        for train in self.fetchAllTrains():
            if train.trainState != 'Active': continue
            total+=1
            howLate = float()
            txt = train.trainTimely
            if 'Late' not in train.trainTimely: continue
            count+=1
            match = re.search(r"^(\d*) Hours?, (\d*) Minutes? Late$", txt)
            if match:
                howLate = (float(match.group(1)) * 60) + float(match.group(2))
            else:
                match = re.search(r"(\d*) Minutes? Late$", txt)
                if not match:
                    print("NO MATCH")
                    exit(0)
                else:
                    howLate = float(match.group(1))
            allLateness.append(howLate)

            if howLate > latestTime:
                latestTime = howLate
                latestTrain = train

        if plot:
            binlow = 0
            binhigh = round(max(allLateness), -1) + 10
            plt.hist( allLateness, bins=int(binhigh/10), range=[binlow, binhigh])
            plt.ylabel(r'$N_{trains}$', loc='top')
            plt.xlabel('Minutes')
            plt.xticks( np.arange(binlow, binhigh, step=30))
            plt.title('Amtrak Late Trains', fontweight='bold', loc='left')
            plt.title(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), loc="right")
            plt.show()

        print(f'{count} / {total} trains are late')
        print(f'{latestTrain.routeName} from {latestTrain.origName} towards {latestTrain.destName} is {latestTrain.trainTimely}')
        return latestTrain, latestTrain.trainTimely

    def fetchFastestTrain( self, plot=False):
        fastestTrain = Struct()
        fastestVelocity = -1
        allVelocities = []
        
        for train in self.fetchAllTrains():
            if train.trainState != 'Active': continue
            howFast = train.velocity
            allVelocities.append( howFast)
            if howFast > fastestVelocity:
                fastestVelocity = howFast
                fastestTrain = train

        print(f'{fastestTrain.routeName} from {fastestTrain.origName} towards {fastestTrain.destName} is travelling {round(fastestVelocity, 2)} mph')
        
        if plot:
            binlow = 0
            binhigh = round(max(allVelocities), -1) + 10
            plt.hist( allVelocities, bins=int(binhigh/10), range=[binlow, binhigh])
            plt.ylabel(r'$N_{trains}$', loc='top')
            plt.xlabel('Velocity (mph)')
            # plt.xticks( np.arange(binlow, binhigh, step=25))
            plt.title('Velocity of Amtrak Trains', fontweight='bold', loc='left')
            plt.title(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), loc="right")
            plt.show()
            
        return fastestTrain, fastestTrain.trainTimely
    
def main():
    amtrak = Amtrak()

    latestTrain, howLate = amtrak.fetchTrainPerformance()
    
    for station in latestTrain.stations:
        if station['status'] != 'Departed':
            print(f"Next Station: {station['name']}")
            break

    print()
    fastestTrain, howFast = amtrak.fetchFastestTrain( plot=True)
        

if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    except KeyboardInterrupt as e:
        print("You've interrupted me :(")
