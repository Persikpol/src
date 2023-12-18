import math
import numpy as np
import matplotlib.pyplot as plt
import csv

latitude = 45.6                    # Широта точки старта, град.
i_target = 0                        # Наклонение ГСО, град.
i_p = 0                             # Поворот орбиты в перигее, град.
mu_Earth = 398600                   # Гравитационный параметр Земли, км^3/c^2
R_Earth = 6371                      # Радиус Земли, км
h_p = 200                           # Высота перигея переходной орбиты, км
h_a = 35793                         # Высота апогея переходной орбиты, км
r_p = R_Earth + h_p                 # Радиус переходной орбиты в перигее, км
r_a = R_Earth + h_a                 # Радиус переходной орбиты в апогее, км
m_top = 6550                        # Масса топлива, кг
m_PN = 5000                         # Масса КА
m_RB = 7640                         # Масса РБ
M_0 = m_RB + m_PN                   # Масса ПН (РБ + КА), кг
I = 333.2 * 9.81/1000               # Удельный импульс, км/с
dict_i_speed = []
azimuth = 0                         # Азимут, град.
i_support_array = []
first_speed_space = math.sqrt(6.67 * math.pow(10, -11) * 5.97 * math.pow(10, 24) / (R_Earth * 1000 + h_p * 1000))/1000  #Первая космическая скорость, км/с


while azimuth <= 90:        # Нахождение минимального угла наклонения опорной орбиты при изменение азимута
    i_support = math.acos(math.sin(azimuth  * math.pi/180) * math.cos(latitude * math.pi/180))
    azimuth = azimuth + 0.5
    i_support_array.append(i_support * 180 / math.pi)
i_support = min([x for x in i_support_array])
print("Минимальное наклонение опорной орбиты - ", round(i_support, 1))

delta_i = round(i_support - i_target, 1)      # Изменение наклонения орбиты КА, град.


def increase_speed_in_per(angle):   # Формула необходимого увеличения скорости в перигее
    angle = angle * math.pi/180
    a = mu_Earth/r_p
    d = math.sqrt(2/(1 + (r_p/r_a)))
    b = math.pow((d-1), 2)
    f = math.pow((math.sin(angle/2)), 2)
    c = 4 * d * f
    delta_V_p = math.sqrt(a) * math.sqrt(b + c)
    return round(delta_V_p, 7)


def increase_speed_in_ap(delta_angle, angle):   # Формула необходимого увеличения скорости в апогее
    angle = angle * math.pi/180
    delta_angle = delta_angle * math.pi/180
    d = math.sqrt(2/(1 + (r_a/r_p)))
    a = mu_Earth/r_a
    b = math.pow((1 - d), 2)
    f = math.pow((math.sin((delta_angle - angle)/2)), 2)
    c = 4 * d * f
    delta_V_a = math.sqrt(a) * math.sqrt(b + c)
    return round(delta_V_a, 7)


def sum_speed(f_1, f_2):            # Импульсная скорость перехода, км/с
    sum_V = f_1 + f_2
    return round(sum_V, 4)


def fuel_consumption(M_0, speed):             # Необходимая масса топлива на перелет с минимальной импульсной скоростью
    m_t = M_0 * (1 - math.exp((-speed)/I))
    m_t = round(m_t)
    return m_t

# m_PG_array = []
# m_t_array = []
def search_m_PN(m_t, m_PG, speed):                  # Подбор массы КА для перелета
    while(m_top < m_t):
        m_PG = m_PG - step
        # m_PG_array.append(m_PG)
        M_start = m_RB + m_PG
        m_t = fuel_consumption(M_start, speed)
        # m_t_array.append(m_t)
    print('Допустимая масса КА для перелета с опорной орбиты на ГСО = ', m_PG, '\n Израсходованное топливо РБ составит, кг : ', m_t)
    return(int(m_PG))


for i in np.arange(i_p, 10 + 0.2, 0.2):    # Нахождение оптимального угла поворота в перигее
    increase_speed_in_per(i)
    increase_speed_in_ap(delta_i, i)
    dict_i_speed.append({'speed': sum_speed(increase_speed_in_per(i), increase_speed_in_ap(delta_i, i)), 'i_p': round(i, 7), 'i_a': round(delta_i - i, 7)})

print('Итерации расчета оптимального угла поворота в перигее переходной орбиты для двухимпульсного перелета')
for elem in dict_i_speed:
    print(elem)

min_speed = min([x['speed'] for x in dict_i_speed])
print("Минимальная импульсная скорость, необходимая для перелета: ", min_speed)
optimum_i = [x['i_p'] for x in dict_i_speed if x['speed'] == min_speed][0]
print("Оптимальный угол: ", optimum_i)

speed_array = [x['speed'] for x in dict_i_speed]
i_p_array = [x['i_p'] for x in dict_i_speed]


print('Масса топлива для перелета с минимальной скоростью: ', fuel_consumption(M_0, min_speed))
step = int(input("Задайте шаг уменьшения массы КА - "))
search_m_PN(fuel_consumption(M_0, min_speed), m_PN, min_speed)

# График зависимости скорости от угла поворота в перигее
plt.plot(i_p_array, speed_array)
plt.grid()
plt.xlabel("Угол поворота в перигее, град.")
plt.ylabel("Суммарная импульсная скорость, км/с")
plt.show()

# # График зависимости массы топлива от массы ПН
# plt.plot(m_PG_array, m_t_array)
# plt.grid()
# plt.xlabel("Масса ПН, кг")
# plt.ylabel("Масса топлива РБ, кг")
# plt.show()

# Трехимпульсный перелет

time_array = []
height_array = []

def speed_three_impulse(delta_angle, angle1, angle2, r_ap):      # Апогей переходных эллиптических орбит, км
    r_n = r_p               # Радиус низшей орбиты
    r_v = r_a               # Радиус высшей орбиты          
    r_otn = r_v/r_n
    r_ap_otn = r_ap/r_n
    angle1 = angle1 * math.pi/180
    angle2 = angle2 * math.pi/180
    delta_angle = delta_angle * math.pi/180
    a1 = (1 + 3 * r_ap_otn)/(1 + r_ap_otn)
    a2 = math.sqrt(2 * r_ap_otn/(1 + r_ap_otn))
    a = math.sqrt(a1 - 2 * a2 * math.cos(angle1))
    b1 = 2 / (1 + r_ap_otn) + 2 * r_otn / (r_otn + r_ap_otn)
    b2 = math.sqrt(r_otn / (1 + r_ap_otn) / (r_otn + r_ap_otn))
    b = 1/math.sqrt(r_ap_otn) * math.sqrt(b1 - 4 * b2 * math.cos(delta_angle - angle1 - angle2))
    c1 = (r_otn + 3 * r_ap_otn) / (r_otn + r_ap_otn)
    c2 = math.sqrt(2 * r_ap_otn / (r_otn + r_ap_otn))
    c = 1/math.sqrt(r_otn) * math.sqrt(c1 - 2 * c2 * math.cos(angle2))
    sum_speed = a + b + c
    finally_speed = sum_speed * first_speed_space
    return round(finally_speed, 4)


for j in range(80000, 400000, 60000):
    dict_three_impulse = []
    print("Оптимизация для высоты апогея орбиты заброса, равной ", j)
    
    for i in np.arange(0, 6.5, 0.5):    # Нахождение оптимального угла поворота в перигее
        dict_three_impulse.append({'massa': int(search_m_PN(fuel_consumption(M_0, speed_three_impulse(delta_i, optimum_i, i, j)), m_PN, speed_three_impulse(delta_i, optimum_i, i, j))),'speed': speed_three_impulse(delta_i, optimum_i, i, j), 'i_3': round(i, 2), 'i_2': round((delta_i - i - 2.6), 2)})
    for elem in dict_three_impulse:
        print(elem)
    min_speed_2 = min([x['speed'] for x in dict_three_impulse])
    print("Минимальная импульсная скорость, необходимая для перелета: ", min_speed_2)
    print('Масса топлива для перелета с минимальной скоростью: ', fuel_consumption(M_0, min_speed_2))
    step = int(input("Задайте шаг уменьшения массы КА - "))
    search_m_PN(fuel_consumption(M_0, min_speed_2), m_PN, min_speed_2)
    
    path = 'three_impulse_' + str(j) + '.csv'
    with open(path,'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('massa','speed','i_3','i_2'))

        for elem in dict_three_impulse:
            writer.writerow((elem['massa'],elem['speed'],elem['i_3'],elem['i_2']))
    
    a = (j + 2 * R_Earth + h_p) / 2
    T1 = round(2 * math.pi * math.sqrt(math.pow(a, 3) / mu_Earth)/3600/2)
    a = (j + 2 * R_Earth + h_a) / 2
    T2 = round(2 * math.pi * math.sqrt(math.pow(a, 3) / mu_Earth)/3600/2)
    T = T1 + T2
    time_array.append(T)
    height_array.append(j)

# print('Время перелета: ', time_array)
# График зависимости скорости от угла поворота в перигее
plt.plot(height_array, time_array)
plt.grid()
plt.xlabel("Высота апогея переходной орбиты, км ")
plt.ylabel("Время перелета, ч")
plt.show()

# Версия для первого и третьего угла, равных нулю

# dict_three_impulse = []
# for j in range(150000, 600000, 60000):
#     dict_three_impulse.append({'speed': speed_three_impulse(delta_i, 0, delta_i, j), 'r_a': j})

# for elem in dict_three_impulse:
#         print(elem)
# min_speed_2 = min([x['speed'] for x in dict_three_impulse])
# print("Минимальная импульсная скорость, необходимая для перелета: ", min_speed_2)
# print('Масса топлива для перелета с минимальной скоростью: ', fuel_consumption(M_0, min_speed_2))
# step = int(input("Задайте шаг уменьшения массы КА - "))
# search_m_PN(fuel_consumption(M_0, min_speed_2), m_PN, min_speed_2)
    
# three_speed_array = [x['speed'] for x in dict_three_impulse]
# r_a_array = [x['r_a'] for x in dict_three_impulse]

# plt.plot(r_a_array, three_speed_array)
# plt.grid()
# plt.xlabel("Радиус переходной орбиты, км")
# plt.ylabel("Суммарная импульсная скорость, км/с")
# plt.show()


        
    
