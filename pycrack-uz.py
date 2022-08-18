
import platform
from colorama import *
import json
import os
from binascii import a2b_hex, b2a_hex
from pywd import MakeAB, MakeMIC
from time import sleep

whichSys = platform.system()
clearCMD = 'cls' if whichSys == "Windows" else "clear"
editor = 'notepad' if whichSys == "Windows" else "nano"

os.system('cls')


def loadWordlist(filename):
    print(Fore.LIGHTCYAN_EX +
          '[*] Loading password list '+filename+'...'+Fore.RESET)
    sleep(0.5)
    with open(filename) as f:
        return [l.strip() for l in f]


passList = loadWordlist("wordlist/rockH100T100.txt")


def CheckHash(ESSID, BSSID, ANonce, SNonce, DATA_FRAMES, MIC):
    PSK = "12345678"
    sleep(0.5)
    print(Fore.LIGHTCYAN_EX + '\n[*] Runnings Test...'+Fore.RESET)

    A, B = MakeAB(aNonce=ANonce, sNonce=SNonce, apMac=BSSID, cliMac=STA)

    mics, PTK, PMK = MakeMIC(
        pwd=PSK,
        ssid=ESSID,
        A=A,
        B=B,
        data=DATA_FRAMES,
    )
    pmkStr = b2a_hex(PMK).decode().upper()
    sleep(0.5)
    print(Fore.LIGHTCYAN_EX + "[*] Generating PMK"+Fore.RESET)
    sleep(0.5)
    print(Fore.LIGHTCYAN_EX + "[*] Calculating MICs"+Fore.RESET)
    mics_decoded = list(map(lambda x: b2a_hex(x).upper().decode()[:-8], mics))
    sleep(0.5)
    print("\nPairwise Master Key: ", pmkStr)
    for i, m in enumerate(mics_decoded):
        sleep(0.5)
        print("\nACTUAL MIC{}   : {}".format(i + 1, MIC[i].upper()))
        if m == MIC[i].upper():
            print(Fore.LIGHTGREEN_EX +
                  "COMPUTED MIC{} : {}".format(i+1, m) +
                  Fore.RESET)
        else:
            print(Fore.LIGHTRED_EX +
                  "COMPUTED MIC{} : {}".format(i+1, m) +
                  Fore.RESET)


def CrackPwds(ESSID, ANonce, SNonce, DATA_FRAMES, MIC):
    print("\n")
    print(Fore.LIGHTCYAN_EX + "[*] Crack Password..."+Fore.RESET)
    A, B = MakeAB(aNonce=ANonce, sNonce=SNonce, apMac=BSSID, cliMac=STA)
    Captured_MIC1, Captured_MIC2, Captured_MIC3 = MIC
    Captured_DATA1, Captured_DATA2, Captured_DATA3 = DATA_FRAMES
    # passList = []
    for i, p in enumerate(passList):
        sleep(1)
        print(Fore.YELLOW + "[*] [{}/{}] Testing Password ".format(
            str(i+1), str(len(passList)))+Fore.RED+p+Fore.RESET)

        m1, _, _ = MakeMIC(
            pwd=p,
            ssid=ESSID,
            A=A,
            B=B,
            data=[Captured_DATA1],
        )
        mic1 = b2a_hex(m1[0]).decode()[:-8]
        if mic1 != Captured_MIC1:
            continue

        m2, _, _ = MakeMIC(
            pwd=p,
            ssid=ESSID,
            A=A,
            B=B,
            data=[Captured_DATA2],
        )
        mic2 = b2a_hex(m2[0]).decode()[:-8]
        if mic2 != Captured_MIC2:
            continue

        m3, _, _ = MakeMIC(
            pwd=p,
            ssid=ESSID,
            A=A,
            B=B,
            data=[Captured_DATA3],
        )
        mic3 = b2a_hex(m3[0]).decode()[:-8]
        if mic3 != Captured_MIC3:
            continue
        sleep(0.5)
        print(Fore.LIGHTGREEN_EX +
              '\nPASSWORD FOUND: ' + p + Fore.RESET)
        sleep(0.5)
        print('\nCaptured MIC1: ' + Captured_MIC1)
        print(Fore.GREEN + 'Computed MIC1: ' +
              mic1+Fore.RESET, end='\n\n')
        print('Captured MIC2: ' + Captured_MIC2)
        print(Fore.GREEN + 'Computed MIC1: ' +
              mic2+Fore.RESET, end='\n\n')
        print('Captured MIC3: ' + Captured_MIC3)
        print(Fore.GREEN + 'Computed MIC1: ' +
              mic3+Fore.RESET, end='\n\n')
        return p
    return None


if __name__ == "__main__":
    print(Style.RESET_ALL)
    clear = "cls" if platform.system() == "Windows" else "clear"
    print(Fore.YELLOW+"[*] Add Your Data To The JSON File"+Fore.RESET)
    sleep(1)
    os.system(editor+" wifi-data.json")
    try:
        print(Fore.YELLOW+"[*] Extracting JSON File"+Fore.RESET)
        capturedData = json.load(open("wifi-data.json"))
        if len(capturedData) == 0:
            raise Exception
    except Exception as e:
        print(Back.RED + "[!] JSON File is Empty"+Back.RESET)
        exit(0)

    before_shake = capturedData["before_shake"]
    first_shake = capturedData["first_shake"]
    second_shake = capturedData["second_shake"]
    third_shake = capturedData["third_shake"]
    fourth_shake = capturedData["fourth_shake"]

    ESSID = before_shake['ESSID']  # Same as SSID
    BSSID = a2b_hex(before_shake['BSSID'])  # Same as AP MAC
    STA = a2b_hex(before_shake['STA'])  # Same as Client Mac

    ANonce = a2b_hex(first_shake['ANonce'])

    SNonce = a2b_hex(second_shake['SNonce'])
    MIC = [
        (second_shake['MIC']),
        (third_shake['MIC']),
        (fourth_shake['MIC']),
    ]

    DATA_FRAMES = [
        a2b_hex(second_shake['DATA_FRAME']),
        a2b_hex(third_shake['DATA_FRAME']),
        a2b_hex(fourth_shake['DATA_FRAME']),
    ]
    try:
        CheckHash(ESSID, BSSID, ANonce, SNonce, DATA_FRAMES, MIC)
    except Exception as e:
        print(Back.RED + "[!] Function Check Hash Broken...", end="")
        sleep(0.5)
        print(" ( "+str(e)+" )  "+Back.RESET)

    try:
        CrackPwds(ESSID, ANonce, SNonce, DATA_FRAMES, MIC)
    except Exception as e:
        print(Back.RED + "[!] Function Check Hash Broken...", end="")
        sleep(0.5)
        print(" ( "+str(e)+" )"+Back.RESET)
