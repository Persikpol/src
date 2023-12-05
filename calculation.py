import math
import numpy as np
import matplotlib.pyplot as plt
import csv

latitude = 45.62                    # Широта точки старта, град.
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


while azimuth <= 90:        # Нахождение минимального угла наклонения опорной орбиты при изменение азимута
    i_support = math.acos(math.sin(azimuth  * math.pi/180) * math.cos(latitude * math.pi/180))
    azimuth = azimuth + 0.5
    i_support_array.append(i_support * 180 / math.pi)
i_support = min([x for x in i_support_array])
print("Минимальное наклонение опорной орбиты - ", i_support)

delta_i = i_support - i_target      # Изменение наклонения орбиты КА, град.


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


def speed_three_impulse(angle1, angle2, r_ap):      # Апогей переходных эллиптических орбит, км
    r_n = r_p               # Радиус низшей орбиты
    r_v = r_a               # Радиус высшей орбиты          
    r_otn = r_v/r_n
    r_ap_otn = r_ap/r_n
    a1 = (1 + 3 * r_ap_otn)/(1 + r_ap_otn)
    a2 = math.sqrt(2 * r_ap_otn/(1 + r_ap_otn))
    a = math.sqrt(a1 - 2 * a2 * math.cos(angle1))
    b1 = 2 / (1 + r_ap_otn) + 2 * r_otn / (r_otn + r_ap_otn)
    b2 = math.sqrt(r_otn / (1 + r_ap_otn) / (r_otn + r_ap_otn))
    b = 1/math.sqrt(r_ap_otn) * math.sqrt(b1 - 4 * b2 * math.cos(angle2))
    c1 = (r_otn + 3 * r_ap_otn) / (r_otn + r_ap_otn)
    c2 = math.sqrt(2 * r_ap_otn / (r_otn + r_ap_otn))
    c = 1/math.sqrt(r_otn) * math.sqrt(c1 - 2 * c2 * math.cos(delta_i - angle1 - angle2))
    sum_speed = a + b + c
    return round(sum_speed, 4)


for j in range(80000, 400000, 60000):
    dict_three_impulse = []
    print("Оптимизация для высоты апогея орбиты заброса, равной ", j)
    for i in np.arange(0, 10 + 0.2, 0.2):    # Нахождение оптимального угла поворота в перигее
        dict_three_impulse.append({'speed': speed_three_impulse(optimum_i, i, j), 'i_2': round(i, 2), 'i_3': round((delta_i - i), 2)})
    for elem in dict_three_impulse:
        print(elem)
    min_speed_2 = min([x['speed'] for x in dict_three_impulse])
    print("Минимальная импульсная скорость, необходимая для перелета: ", min_speed_2)
    print('Масса топлива для перелета с минимальной скоростью: ', fuel_consumption(M_0, min_speed_2))
    step = int(input("Задайте шаг уменьшения массы КА - "))
    search_m_PN(fuel_consumption(M_0, min_speed_2), m_PN, min_speed_2)
    path = 'three_impulse_' + str(j) + '.csv'
    with open(path,'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('speed','i_2','i_3'))

        for elem in dict_three_impulse:
            writer.writerow((elem['speed'],elem['i_2'],elem['i_3']))



