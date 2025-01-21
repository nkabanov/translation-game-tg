import pandas
table = pandas.read_csv("slovar.csv")
spisok = [words for words in table["Слово"]]
sinonimi = []

for words in spisok:
        synonimos = [table["Синоним_1"][spisok.index(words)],
                     table["Синоним_2"][spisok.index(words)],
                     table["Синоним_3"][spisok.index(words)],
                     table["Синоним_3"][spisok.index(words)],
                     table["Синоним_4"][spisok.index(words)],
                     ]
        stroka_sinonimov = "Синонимы: "
        new_str = ""
        for sin in range(len(synonimos)):
            try:
                stroka_sinonimov += synonimos[sin] + ", "
            except TypeError:
                po_simvolam = list(stroka_sinonimov)
                po_simvolam.pop(len(po_simvolam) - 2)
                for elem in po_simvolam:
                    new_str += elem
                break

        if len(new_str) > 10:
            sinonimi.append(words)

def Dictionary(slovo):
    q = slovo.upper()
    for words in spisok:
        if q==words:

            synonimos = [table["Синоним_1"][spisok.index(words)],
                         table["Синоним_2"][spisok.index(words)],
                         table["Синоним_3"][spisok.index(words)],
                         table["Синоним_3"][spisok.index(words)],
                         table["Синоним_4"][spisok.index(words)],
                         ]
            stroka_sinonimov="Cинонимы: "
            new_str = ""
            for sin in range(len(synonimos)):
                try:
                    stroka_sinonimov+=synonimos[sin]+", "
                except TypeError:
                    po_simvolam = list(stroka_sinonimov)
                    po_simvolam.pop(len(po_simvolam)-2)
                    for elem in po_simvolam:
                        new_str+=elem
                    break

            if len(new_str)>10:
                return f"{words}\n \n" \
                       f"{table['Перевод'][spisok.index(q)]}\n \n" \
                       f"{table['Употребление'][spisok.index(q)]}\n \n" \
                       f"{table['Значение'][spisok.index(q)]}\n \n" \
                       f"1) {table['Пример_1'][spisok.index(q)]}\n" \
                       f"2) {table['Пример_2'][spisok.index(q)]}\n" \
                       f"3) {table['Пример_3'][spisok.index(q)]}\n \n" \
                       f"{new_str}\n"

            else:
                return f"{words}\n \n" \
                       f"{table['Перевод'][spisok.index(q)]}\n \n" \
                       f"{table['Употребление'][spisok.index(q)]}\n \n" \
                       f"{table['Значение'][spisok.index(q)]}\n \n" \
                       f"1) {table['Пример_1'][spisok.index(q)]}\n" \
                       f"2) {table['Пример_2'][spisok.index(q)]}\n" \
                       f"3) {table['Пример_3'][spisok.index(q)]}\n"

    else:
        return "Ничего не найдено"

def Znachenie(slovo):
    q = slovo.upper()
    for words in spisok:
        if q==words:

            new_str = ""
            if len(new_str)>10:
                return f"{table['Значение'][spisok.index(q)]}\n \n"
            else:
                return f"{table['Значение'][spisok.index(q)]}\n \n"

    else:
        return "Ничего не найдено"

def Usage(slovo):
    q = slovo.upper()
    for words in spisok:
        if q==words:

            new_str = ""
            if len(new_str)>10:
                return f"{table['Пример_1'][spisok.index(q)]}\n"
            else:
                return f"{table['Пример_1'][spisok.index(q)]}\n"

    else:
        return "Ничего не найдено"

def Synonyms(slovo):
    q = slovo.upper()
    for words in spisok:
        if ((q == words) and (table[f"Синоним_1"][spisok.index(words)]) != ''):
            synonimos = [table[f"Синоним_{i}"][spisok.index(words)] for i in range(1, 5)]
            synonimos = [s for s in synonimos if isinstance(s, str)]
            return ", ".join(synonimos)
    return "Ничего не найдено"
def Poisk_po_bukvam(letter):
    slova_na_bukvu = []
    for words in spisok:
        if words[0]==letter:
            slova_na_bukvu.append(words)
    return slova_na_bukvu