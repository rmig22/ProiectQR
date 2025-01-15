from PIL import Image


def process_qr_image("ScanGogh.png", threshold=128):
    """
    Procesează un fișier PNG și separă albul de negru într-o matrice binară.
    :param filename: Calea către fișierul PNG.
    :param threshold: Prag pentru conversia alb/negru (0-255).
    :return: Matrice binară (listă de liste cu 0 și 1).
    """
    image = Image.open("ScanGogh.png").convert("L")  # Conversie în grayscale
    width, height = image.size
    binary_matrix = []

    # Parcurgem fiecare pixel
    for y in range(height):
        row = []
        for x in range(width):
            pixel = image.getpixel((x, y))
            row.append(1 if pixel < threshold else 0)  # Negru = 1, Alb = 0
        binary_matrix.append(row)

    return binary_matrix


def display_matrix(matrix):
    """
    Afișează o matrice binară în consolă, utilizând simboluri vizuale.
    :param matrix: Matrice binară (listă de liste cu 0 și 1).
    """
    for row in matrix:
        print("".join("█" if cell else " " for cell in row))


# Exemplu de utilizare
binary_qr = process_qr_image("qr_code.png")
display_matrix(binary_qr)