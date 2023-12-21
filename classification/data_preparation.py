import os
import pandas as pd
import math

adresses = [
    'data/YouTube_CSV/1_Wildlife/',
    'data/YouTube_CSV/2_Dynasties/',
    'data/YouTube_CSV/3_Big_Bang/',
    'data/YouTube_CSV/4_UK_National_Parks/',
    'data/YouTube_CSV/5_Mate_or_die_trying/',
    'data/YouTube_CSV/6_Where_Are_the_Stars/',
    'data/YouTube_CSV/7_Filming_Wildlife_Documentary/',
    'data/YouTube_CSV/8_Fireflies/',
    'data/YouTube_CSV/9_Seven_Worlds/',
    'data/YouTube_CSV/10_Uncover_Antarctica/',
    'data/YouTube_CSV/11_What_Sperm_Whales/',
    'data/YouTube_CSV/12_Everest_Biology/',
    'data/YouTube_CSV/13_Mapping_the_Highest_Peak/',
    'data/YouTube_CSV/14_Meet_the_Worlds_Tiniest_Trees/',
    'data/YouTube_CSV/15_What_To_Do/',
    'data/YouTube_CSV/16_Everest_Weather/',
    'data/YouTube_CSV/17_What_Mud_From_Glacial_Lakes/',
    'data/YouTube_CSV/18_Everest_Glaciology/',
    'data/YouTube_CSV/19_Plants_Dying/',
    'data/YouTube_CSV/20_Macaroni_Penguins/',
    'data/YouTube_CSV/21_Go_Inside_an_Antarctic_City/',
    'data/YouTube_CSV/22_Snow_Leopards/',
    'data/YouTube_CSV/23_Saving_the_Florida_Wildlife_Corridor/',
    'data/YouTube_CSV/24_Wolf_Pack_Takes_on_a_Polar_Bear/',
    'data/YouTube_CSV/25_Last_Wild_Places/'
]

def density_counter(quality):

    time_unit = 1

    d = {'Video_number': [], 'Density_burst': [], 'Density_throttling': []}
    for i in range(len(adresses)):
        data = pd.read_csv(adresses[i] + quality + '.csv')
        max_time = data['Time'].iat[-1] - data['Time'].iat[0]
        time_units = math.ceil(max_time / time_unit)
        lengths = [0] * time_units
        for index, row in data.iterrows():
            lengths[math.floor(row['Time'] / time_unit)] += row['Length']

        # получили массив длин, надо вычислить расположение первоначального пика
        # и вычислить Density_burst и Density_throttling
            
        difference_pos = 0
        
        # 40 секунд, за которые точно успевает пройти burst
        burst_max_time = 40
        if time_units - 1 < 40:
            burst_max_time = time_units - 1
        
        # 1 способ: если есть отрезок с нулевой передаваемой длиной
        for j in range(burst_max_time // time_unit):
            if (difference_pos == 0 and lengths[j + 1] == 0):
                difference_pos = j + 1

        # 2 способ: если столбец отличается в 3 раза от следующего
        if difference_pos == 0:
            coeff = 3
            for j in range(burst_max_time // time_unit):
                if lengths[j] != 0 and lengths[j + 1] != 0 and lengths[j] > lengths[j + 1] * coeff:
                    difference_pos = j + 1
                    coeff = lengths[j] / lengths[j + 1]
        
        # 3 способ: поиск зоны с наибольшей разницей плотности
        if difference_pos == 0:
            difference = 0
            for j in range(1, time_units):
                first_sum = 0
                second_sum = 0
                for k in range(0, j):
                    first_sum += lengths[k]
                for l in range(j, time_units):
                    second_sum += lengths[l]
                if first_sum / j - second_sum / (time_units - j) > difference:
                    difference = first_sum / j - second_sum / (time_units - j)
                    difference_pos = j
        
        # Вычислили расположение первоначального пика, остались density_burst и density_throttling

        density_burst = 0
        density_throttling = 0
        for p in range(0, difference_pos):
            density_burst += lengths[p]
        for q in range(difference_pos, time_units):
            density_throttling += lengths[q]
        density_burst = density_burst / (difference_pos * time_unit)
        density_throttling = density_throttling / ((time_units - difference_pos) * time_unit)

        num_spaces = len(str(int(density_burst))) - len(str(int(density_throttling)))
        
        d['Video_number'].append(i + 1)
        d['Density_burst'].append(density_burst)
        d['Density_throttling'].append(density_throttling)
        
    return d

if __name__ == "__main__":

    print("Starting data preparation")

    df_4K = pd.DataFrame(data=density_counter('4K'))
    df_1440 = pd.DataFrame(data=density_counter('1440'))
    df_1080 = pd.DataFrame(data=density_counter('1080'))
    df_720 = pd.DataFrame(data=density_counter('720'))
    df_480 = pd.DataFrame(data=density_counter('480'))
    df_360 = pd.DataFrame(data=density_counter('360'))

    df_4K["Quality"] = "2160"
    df_1440["Quality"] = "1440"
    df_1080["Quality"] = "1080"
    df_720["Quality"] = "720"
    df_480["Quality"] = "480"
    df_360["Quality"] = "360"

    data = pd.concat([df_4K, df_1440, df_1080, df_720, df_480, df_360], ignore_index=True)

    data.to_csv('data.csv')  

    print("Data saved to data.csv")
