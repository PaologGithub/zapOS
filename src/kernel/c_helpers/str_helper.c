int get_string_len(char string[]) {
    int len = 0;

    while (string[len] != '\0') {
        len++;
    }

    return len;
}

char get_char_at(char string[], int i) {
    return string[i];
}