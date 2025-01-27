####################
####################
#  PROIECT COD QR  #
####################
####################

# Scriere cod QR

import reedsolo

def generare_ecc(M, capacitate):

    # https://pypi.org/project/reedsolo/#basic-usage-with-high-level-rscodec-class
    # mare chin cu ECC ul

    rs = reedsolo.RSCodec(capacitate)

    for linie in M:
        stringul = bytearray(int(linie[0][i:i + 8], 2) for i in range(0, len(linie[0]), 8))

        stringcuECC = rs.encode(stringul)

        ECC = stringcuECC[len(stringul):]

        ECCinbinar = "".join(format(byte, '08b') for byte in ECC)

        linie[1] = ECCinbinar

def scrierecodQR():
    print()
    secv = input("Sirul de caractere ce doresti a transforma in cod QR: ")
    secv = secv.strip()

    # din https://www.nayuki.io/page/creating-a-qr-code-step-by-step

    # Ce versiune sa folosim? (Error correction high)

    # Max V6
    VE = [0, 9, 16, 26, 36, 46, 60]         # Capacitatile in functie de versiune
    VECC = [0, 17, 28, 22, 16, 22, 28]      # ECC urile in functie de versiune
    VnrB = [0, 1, 1, 2, 4, 4, 4]            # Numarul de blocuri in functie de versiune

    # 1. Create data segment
    secv = list(secv)
    for i in range(len(secv)):
        # tranformam fiecare caracter in cod ascii
        secv[i] = ord(secv[i])
        # transformam fiecare cod ascii in binar
        secv[i] = bin(secv[i])

    # 2.Fit to version number
    # Segment 0 count
    segmlen = len(secv)
    segmlen = bin(segmlen)

    # 3. Concatenate segments, add padding, make codewords
    Segment_0_mode = "0100"                 # corespunde modului byte
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

    nr_pana_acum = Segment_0_mode + segmlen + Segment_0_data + terminator

    aux = len(nr_pana_acum)
    while aux % 8 != 0:
        nr_pana_acum += "0"
        aux = len(nr_pana_acum)
        print("DA")

    aux = aux//8                            # nr de caractere curente

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

    nrBlocuri = VnrB[vs]

    nrDataCodeWords = len(nr_pana_acum)//8
    dataCdWdperLB = nrDataCodeWords//4 + 1                  # Data codewords per long block

    if nrDataCodeWords % nrBlocuri != 0:
        dataCdWdperLB = nrDataCodeWords // nrBlocuri + 1    # Data codewords per long block
        dataCdWdperSB = dataCdWdperLB - 1                   # Data codewords per short block
    else:
        dataCdWdperLB = nrDataCodeWords // nrBlocuri        # Data codewords per long block
        dataCdWdperSB = dataCdWdperLB

    aux = nrDataCodeWords % nrBlocuri
    if aux == 0:
        nrLB = nrBlocuri                        # Nr Long Blocks
        nrSB = 0                                # Nr Short Blocks
        copnrLB = nrLB
        copnrSB = nrSB
    else:
        nrLB = aux
        copnrLB = nrLB
        nrSB = nrBlocuri - aux
        copnrSB = nrSB

    nr_pana_acum = list(nr_pana_acum)

    for i in range(0,len(nr_pana_acum),8):
        nr_pana_acum[i] = "".join(nr_pana_acum[i:i+8])

    while "0" in nr_pana_acum:
        nr_pana_acum.remove("0")
    while "1" in nr_pana_acum:
        nr_pana_acum.remove("1")

    M = []                                      # matricea in care stocam datele

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

    for i in range(len(M)):
        M[i] = [M[i], []]

    generare_ecc(M, VECC[vs])

    for i in range(len(M)):
        for j in range(0,len(M[i])):
            M[i][j] = list(M[i][j])
            for k in range(0,len(M[i][j]),8):
                M[i][j][k] = "".join(M[i][j][k:k+8])
            while "0" in M[i][j]:
                M[i][j].remove("0")
            while "1" in M[i][j]:
                M[i][j].remove("1")

    M2 = []                                     # Matricea cu elementele reasezate

    copnrLB = nrLB
    copnrSB = nrSB - 1

    if dataCdWdperLB != dataCdWdperSB:
        while copnrSB != -1:
            M[copnrSB][0].append(None)
            copnrSB -= 1

    for i in range(0,len(M)):
        M[i] = M[i][0] + M[i][1]

    M2 = [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]

    for i in range(len(M2)):
        while None in M2[i]:
            M2[i].remove(None)

    M3 = [elem for linie in M2 for elem in linie]       # Lista cu elemente

    print(M3)

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