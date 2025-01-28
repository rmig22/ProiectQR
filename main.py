####################
####################
#  PROIECT COD QR  #
####################
####################

# Scriere cod QR

import reedsolo
from PIL import Image
import numpy as np

def zigzag(QR, M3):

    aux = len(QR)                       # Dim QR
    cnt = 0                             # Contor M3
    directie = -1                       # -1 pentru sus, +1 pentru jos
    j = aux - 1                         # prima pozitie

    while j > 0:
        if j == 6:
            j -= 1

        i = aux - 1 if directie == -1 else 0            # Pornim de jos sau de sus
        while (i >= 0 and directie == -1) or (i < aux and directie == 1):
            for col in [j, j - 1]:
                if cnt == len(M3):
                    return QR

                if not (
                    (i >= aux - 8 and col <= 8) or
                    (i == 6 or col == 6) or
                    (i <= 8 and col <= 8) or
                    (i <= 8 and col >= aux - 8) or
                    (aux - 9 <= i <= aux - 5 and aux - 9 <= col <= aux - 5 and aux != 21)
                ):
                    QR[i][col] = M3[cnt]
                    cnt += 1

            i += directie

        directie *= -1
        j -= 2

    return QR

def matrice_to_png(QR, fisier = "outputASC.png", scale=10):
    # https://stackoverflow.com/questions/78913551/python-using-pillow-to-convert-any-format-to-png-any-way-to-speed-the-process
    # https://www.geeksforgeeks.org/convert-a-numpy-array-to-an-image/

    # Convertire QR -> NumPy
    QR = np.array(QR, dtype=np.uint8)

    # Marim QR (ca sa nu avem un numar = un pixel)
    QR2 = np.kron(QR, np.ones((scale, scale), dtype=np.uint8))

    # 1 = black, 0 = white
    x = (1 - QR2) * 255

    # crearea efectiva
    Image.fromarray(x, mode="L").save(fisier)

    print()
    print(f"Imaginea a fost salvata ca '{fisier}'.")

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
    VQRSize = [0, 21, 25, 29, 33, 37, 41]   # Marimea matricei QR in functie de versiune

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
    M3 = "".join(M3)
    M3 = list(M3)
    for i in range(len(M3)):
        M3[i] = int(M3[i])

    # 5. Draw fixed patterns

    QR = [[0 for _ in range(VQRSize[vs])] for _ in range(VQRSize[vs])]

    for i in range(VQRSize[vs]):
        if i % 2 == 0:
            QR[i][6] = 1
            QR[6][i] = 1

    # Coltul stanga sus

    for i in range(8):
        for j in range(8):
            QR[i][j] = 0

    for i in range(7):
        for j in range(7):
            QR[i][j] = 1

    for i in range(1,6):
        for j in range(1,6):
            QR[i][j] = 0

    for i in range(2,5):
        for j in range(2,5):
            QR[i][j] = 1

    # Coltul dreapta sus

    aux = len(QR)

    for i in range(8):
        for j in range(aux-8,aux):
            QR[i][j] = 0

    for i in range(7):
        for j in range(aux-7,aux):
            QR[i][j] = 1

    for i in range(1, 6):
        for j in range(aux-6, aux-1):
            QR[i][j] = 0

    for i in range(2, 5):
        for j in range(aux-5, aux-2):
            QR[i][j] = 1

    # Coltul stanga jos

    for i in range(aux-8,aux):
        for j in range(8):
            QR[i][j] = 0

    for i in range(aux-7,aux):
        for j in range(7):
            QR[i][j] = 1

    for i in range(aux-6, aux-1):
        for j in range(1, 6):
            QR[i][j] = 0

    for i in range(aux-5, aux-2):
        for j in range(2, 5):
            QR[i][j] = 1

    # patrat dreapta jos

    if vs >= 2:
        for i in range(aux - 9, aux - 4):
            for j in range(aux - 9, aux - 4):
                QR[i][j] = 1

        for i in range(aux - 8, aux - 5):
            for j in range(aux - 8, aux - 5):
                QR[i][j] = 0

        QR[aux-7][aux-7] = 1

    QR[aux-8][8] = 1

    # 6. Draw codewords and remainder

    QR = zigzag(QR,M3)

    # 7. Try applying each mask

    Lista_masti = [[],[],[],[],[],[],[],[]]
    for i in range(len(Lista_masti)):
        Lista_masti[i] = [[0 for _ in range(VQRSize[vs])] for _ in range(VQRSize[vs])]

        for j in range(VQRSize[vs]):
            Lista_masti[i][j][6] = None
            Lista_masti[i][6][j] = None

        # Coltul stanga sus

        for j in range(9):
            for k in range(9):
                Lista_masti[i][j][k] = None

        # Coltul dreapta sus

        aux = len(Lista_masti[i])

        for j in range(9):
            for k in range(aux - 8, aux):
                Lista_masti[i][j][k] = None

        # Coltul stanga jos

        for j in range(aux - 8, aux):
            for k in range(9):
                Lista_masti[i][j][k] = None

        # patrat dreapta jos

        if vs >= 2:
            for j in range(aux - 9, aux - 4):
                for k in range(aux - 9, aux - 4):
                    Lista_masti[i][j][k] = None

    # MASCA 0

    for i in range(len(Lista_masti[0])):
        for j in range(len(Lista_masti[0][i])):
            if Lista_masti[0][i][j] != None:
                if (i+j)%2 == 0:
                    Lista_masti[0][i][j] = 1

    # MASCA 1

    for i in range(len(Lista_masti[1])):
        for j in range(len(Lista_masti[1][i])):
            if Lista_masti[1][i][j] != None:
                if i%2 == 0:
                    Lista_masti[1][i][j] = 1

    # MASCA 2

    for i in range(len(Lista_masti[2])):
        for j in range(len(Lista_masti[2][i])):
            if Lista_masti[2][i][j] != None:
                if j%3 == 0:
                    Lista_masti[2][i][j] = 1

    # MASCA 3

    for i in range(len(Lista_masti[3])):
        for j in range(len(Lista_masti[3][i])):
            if Lista_masti[3][i][j] != None:
                if (i+j)%3 == 0:
                    Lista_masti[3][i][j] = 1

    # MASCA 4

    for i in range(len(Lista_masti[4])):
        for j in range(len(Lista_masti[4][i])):
            if Lista_masti[4][i][j] != None:
                if (
                        ((i%4 == 0 or i%4 == 1) and (j%6 == 0 or j%6 == 1 or j%6 == 2))
                    or
                        ((i%4 == 2 or i%4 == 3) and (j%6 == 3 or j%6 == 4 or j%6 == 5))
                ):
                    Lista_masti[4][i][j] = 1

    # MASCA 5

    for i in range(len(Lista_masti[5])):
        for j in range(len(Lista_masti[5][i])):
            if Lista_masti[5][i][j] != None:
                if (
                        ((i%6 == 0) or (j%6 == 0))
                    or
                        (i%2 == 0 and (j-3)%6 == 0)
                    or
                        (j%2 == 0 and (i-3)%6 == 0)
                ):
                    Lista_masti[5][i][j] = 1

    # MASCA 6

    for i in range(len(Lista_masti[6])):
        for j in range(len(Lista_masti[6][i])):
            if Lista_masti[6][i][j] != None:
                if (
                        ((i % 6 == 0) or (j % 6 == 0))
                    or
                        (i % 2 == 0 and (j - 3) % 6 == 0)
                    or
                        (j % 2 == 0 and (i - 3) % 6 == 0)
                    or
                        ((i+j+3)%6 == 0)
                    or
                        ((i+1)%6 == 0 and (j+1)%6 == 0)
                    or
                        ((i-1)%6 == 0 and (j-1)%6 == 0)
                    or
                        ((i-4)%6 == 0 and (j-2)%6 == 0)
                    or
                        ((i-2)%6 == 0 and (j-4)%6 == 0)

                ):
                    Lista_masti[6][i][j] = 1

    # MASCA 7

    for i in range(len(Lista_masti[7])):
        for j in range(len(Lista_masti[7][i])):
            if Lista_masti[7][i][j] != None:
                if (i+j)%3 == 0:
                    Lista_masti[7][i][j] = 1


    for i in range(len(Lista_masti)):
        print(f"Masca {i}:")
        for j in range(len(Lista_masti[i])):
            print(Lista_masti[i][j])
        print()


    matrice_to_png(QR, "outputASC.png", 20)

    return

# Citire cod QR



def citirecodQR():
    print()
    fisier = input("Fisierul pe care doresti sa il transformi in sir de caractere: ")
    print(fisier)

    SCALE = 20  # Factor de scalare pentru imaginea mărită

    # Dimensiunile diferitelor variante de QR (dimensiune matrice + zone rezervate)
    dimensiuni_qr = {
        1: 21, 2: 25, 3: 29, 4: 33, 5: 37, 6: 41
    }

    def culoare_pixel(img, x, y):
        """Returnează 1 pentru negru și 0 pentru alb, ținând cont de scalare."""
        r, g, b = img.getpixel((x * SCALE, y * SCALE))  # Citim doar pixelul relevant
        return 1 if (r, g, b) == (0, 0, 0) else 0

    def este_zona_rezervata(x, y, versiune):
        """Verifică dacă pixelul (x, y) face parte dintr-o zonă rezervată pentru varianta dată."""
        dim = dimensiuni_qr[versiune]

        # Finder patterns (colțurile stânga-sus, dreapta-sus, stânga-jos)
        if (x < 9 and y < 9) or (x < 9 and y >= dim - 9) or (x >= dim - 9 and y < 9):
            return True

        # Separatoare (linii albe de 1 pixel în jurul finder patterns)
        if x == 6 or y == 6:
            return True

        # Alignment pattern (pentru versiunile 2-6, se află la diferite coordonate)
        if versiune >= 2:
            if 6 <= x <= dim - 7 and 6 <= y <= dim - 7:
                return True

        # Zonele de format (lângă finder patterns)
        if (y == 8 or x == 8) and not (x > 8 and y > 8):
            return True

        return False

    def extrage_bits_qr(img_path, versiune):
        """Extrage secvența de biți dintr-un cod QR, excluzând zonele rezervate, pentru orice variantă."""
        dim = dimensiuni_qr[versiune]
        img = Image.open(img_path).convert('RGB')

        qr_bits = []
        directie = -1  # -1 pentru sus, +1 pentru jos
        j = dim - 1  # Începem din colțul din dreapta jos

        while j > 0:
            if j == 6:  # Sărim coloana de aliniere
                j -= 1

            i = dim - 1 if directie == -1 else 0  # Pornim de jos sau de sus
            while (i >= 0 and directie == -1) or (i < dim and directie == 1):
                for col in [j, j - 1]:
                    if len(qr_bits) == (dim * dim - (dim // 7) * 5):  # Dimensiune finală corectă
                        return "".join(map(str, qr_bits))

                    if not este_zona_rezervata(i, col, versiune):
                        qr_bits.append(culoare_pixel(img, col, i))

                i += directie

            directie *= -1
            j -= 2  # Trecem la următoarea pereche de coloane

        return "".join(map(str, qr_bits))

    def eliminare_ECC(cod):

        # dictionarul cu datele pentru fiecare varianta, toate pe error-correction high
        qr = {
            1: {"marime_biti": 72, "total_bytes+ecc": 26},
            2: {"marime_biti": 128, "total_bytes+ecc": 44},
            3: {"marime_biti": 208, "total_bytes+ecc": 70},
            4: {"marime_biti": 288, "total_bytes+ecc": 100},
            5: {"marime_biti": 368, "total_bytes+ecc": 134},
            6: {"marime_biti": 480, "total_bytes+ecc": 172},
        }
        for versiune in qr.keys():
            if qr[versiune]["total_bytes+ecc"] == len(cod) / 8:
                return cod[:qr[versiune]["marime_biti"]], versiune
        else:
            print("Codul QR este de o varianta > 6")
            return -1, -1

    def rearanjare_cod(string_cod, versiune):

        # facem rearanjarea pentru fiecare tip de varianta
        if versiune == 1 or versiune == 2:
            return string_cod

        elif versiune == 3:
            cod = [string_cod[i:i + 8] for i in range(0, len(string_cod), 8)]
            cod_nou = [[cod[0]], [cod[1]]]

            for i in range(2, len(cod)):
                cod_nou[i % 2].append(cod[i])

            string_cod_nou = "".join("".join(x for x in linie) for linie in cod_nou)
            return string_cod_nou

        elif versiune == 4 or versiune == 6:
            cod = [string_cod[i:i + 8] for i in range(0, len(string_cod), 8)]
            cod_nou = [[cod[0]], [cod[1]], [cod[2]], [cod[3]]]

            for i in range(4, len(cod)):
                cod_nou[i % 4].append(cod[i])

            string_cod_nou = "".join("".join(x for x in linie) for linie in cod_nou)
            return string_cod_nou
        # facem rearanjarea pentru varianta 5
        else:
            cod = [string_cod[i:i + 8] for i in range(0, len(string_cod), 8)]
            cod_nou = [[cod[0]], [cod[1]], [cod[2]], [cod[3]]]

            for i in range(4, len(cod)):
                if i == 44:
                    cod_nou[2].append(cod[i])
                elif i == 45:
                    cod_nou[3].append(cod[i])
                else:
                    cod_nou[i % 4].append(cod[i])

            string_cod_nou = "".join("".join(x for x in linie) for linie in cod_nou)
            return string_cod_nou

    def scapam_11EC(test):
        # formam o matrice cu elemente de 8 biti
        cod = [test[i:i + 8] for i in range(0, len(test), 8)]

        i = len(cod) - 1

        # aici scapam de valorile 11 si EC, plecam de la sfarsit spre inceput
        while i >= 0:
            if cod[i] == "11101100" or cod[i] == "00010001":
                cod.pop(i)
                i -= 1
            else:
                break

        string_cod = "".join(cod)

        # formam o matrice cu elemente de 4 biti
        cod = [string_cod[i:i + 4] for i in range(0, len(string_cod), 4)]

        # aici scapam de cei 4 biti de terminator si de cei 4 biti ai modului segmentului
        cod.pop(0)
        cod.pop()

        string_cod = "".join(cod)
        # formam inapoi o matrice de 8 biti
        cod = [string_cod[i:i + 8] for i in range(0, len(string_cod), 8)]

        # aici scapam de segment 0 count (care are 8 biti pentru versiunile noastre)
        cod.pop(0)

        # aici avem string-ul final, trecerea din binar in string
        s = ''.join(chr(int(linie, 2)) for linie in cod)
        print(s)

    versiune = 4  # Poți schimba versiunea între 1 și 6
    qr_bits = extrage_bits_qr(fisier, versiune)

    # DE AICI MERGE BINE, QR_BITS NU E CORECT GENERAT
    zz = qr_bits

    s, z = eliminare_ECC(zz)
    if s != -1:
        test = rearanjare_cod(s, z)
        scapam_11EC(test)

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