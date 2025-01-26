####################
####################
#  PROIECT COD QR  #
####################
####################

# Scriere cod QR

import reedsolo

def scrierecodQR():
    print()
    secv = input("Sirul de caractere ce doresti a transforma in cod QR: ")
    secv = secv.strip()

    #din https://www.nayuki.io/page/creating-a-qr-code-step-by-step

    #Ce versiune sa folosim? (Error correction high)

    VE = [0,9,16,26,36,46,60] #Max V6

    #1. Create data segment
    secv = list(secv)
    for i in range(len(secv)):
        #tranformam fiecare caracter in cod ascii
        secv[i] = ord(secv[i])
        #transformam fiecare cod ascii in binar
        secv[i] = bin(secv[i])

    #2.Fit to version number
    #Segment 0 count
    segmlen = len(secv)
    segmlen = bin(segmlen)

    #3. Concatenate segments, add padding, make codewords
    Segment_0_mode = "0100"  #corespunde modului byte
    segmlen = str(segmlen)
    segmlen = segmlen[2:]
    while len(segmlen) < 8:
        segmlen = "0" + segmlen

    Segment_0_data = ""

    for i in secv:
        aux = str(i)
        aux = aux[2:]
        aux = aux.zfill(8)
        Segment_0_data = Segment_0_data + aux

    terminator = "0000"

    bit_padding = ""

    nr_pana_acum = Segment_0_mode + segmlen + Segment_0_data + terminator

    aux = len(nr_pana_acum)
    while aux % 8 != 0:
        nr_pana_acum += "0"
        aux = len(nr_pana_acum)
        print("DA")

    aux = aux//8    #nr de caractere curente

    for i in range(len(VE)):
        if aux > VE[i]:
            vs = i
        else:
            vs = i
            break

    capacitate = VE[vs]
    Byte_padding = capacitate-aux

    auxEC = "11101100"
    aux11 = "00010001"

    while Byte_padding != 0:
        nr_pana_acum += auxEC
        Byte_padding -= 1
        if Byte_padding == 0:
            break
        nr_pana_acum += aux11
        Byte_padding -= 1

    # 4. Split blocks, add ECC, interleave

    nrDataCodeWords = len(nr_pana_acum)//8
    dataCdWdperLB = nrDataCodeWords//4 + 1 #Data codewords per long block

    if nrDataCodeWords % 4 != 0:
        dataCdWdperSB = dataCdWdperLB - 1 #Data codewords per short block
    else:
        dataCdWdperSB = dataCdWdperLB

    aux = nrDataCodeWords % 4
    if aux == 0:
        nrLB = 4                #Nr Long Blocks
        nrSB = 0                #Nr Short Blocks
        copnrLB = nrLB
        copnrSB = nrSB
    else:
        nrLB = aux
        copnrLB = nrLB
        nrSB = 4 - aux
        copnrSB = nrSB

    nr_pana_acum = list(nr_pana_acum)

    for i in range(0,len(nr_pana_acum),8):
        nr_pana_acum[i] = "".join(nr_pana_acum[i:i+8])

    while "0" in nr_pana_acum:
        nr_pana_acum.remove("0")
    while "1" in nr_pana_acum:
        nr_pana_acum.remove("1")

    M = [] #matricea in care stocam datele

    for i in range(len(nr_pana_acum)):
        M.append(nr_pana_acum[i])

    i = 0
    while copnrSB != 0:
        x = "".join(M[i:i+dataCdWdperSB])
        M[i:i+dataCdWdperSB] = [x]
        i += 1
        copnrSB -= 1
    while copnrLB != 0:
        x = "".join(M[i:i+dataCdWdperLB])
        M[i:i+dataCdWdperLB] = [x]
        i += 1
        copnrLB -= 1

    print(M)

    return

# Citire cod QR

def citirecodQR():
    print()
    fisier = input("Fisierul pe care doresti sa il transformi in sir de caractere: ")
    print(fisier)
    return

# MENIU

print("Meniu:")

optiune = -1

while optiune != 1 and optiune != 2 and optiune != 3:
    print()
    print("1) Scriere cod QR")
    print("2) Citire cod QR")
    print("3) Iesire din program\n")

    optiune = int(input("Ce optiune alegi: "))

    if optiune != 1 and optiune != 2 and optiune != 3:
        print("\nEroare, optiune gresita, mai incercati!\n")

    if optiune == 1:
        optiune = 0 # PENTRU A RULA CONTINUU PROGRAMUL
        scrierecodQR()
    if optiune == 2:
        optiune = 0 # PENTRU A RULA CONTINUU PROGRAMUL
        citirecodQR()