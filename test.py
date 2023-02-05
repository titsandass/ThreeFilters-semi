import pickle

def save_CA_pickle2txt(CApikcleFilePath):
    with open('ca_multiprocess.pickle', 'rb') as f:
        CAResults = pickle.load(f)
    with open('ca_multiprocess_5200.pickle', 'rb') as f:
        CAResults2 = pickle.load(f)
    with open('ca_multiprocess_1400.pickle', 'rb') as f:
        CAResults3 = pickle.load(f)
    with open(CApikcleFilePath.replace('.pickle','.txt'), 'w') as f:
        for CAResult in CAResults:
            for CA in CAResult:
                print(*CA, sep='\t', file=f)
    with open(CApikcleFilePath.replace('.pickle','2.txt'), 'w') as f:
        for CAResult in CAResults2:
            for CA in CAResult:
                print(*CA, sep='\t', file=f)
    with open(CApikcleFilePath.replace('.pickle','3.txt'), 'w') as f:
        for CAResult in CAResults3:
            for CA in CAResult:
                print(*CA, sep='\t', file=f)                                

CApikcleFilePath = 'ca_multiprocess.pickle'
save_CA_pickle2txt(CApikcleFilePath)
pass