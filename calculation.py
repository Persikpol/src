import math
import numpy as np
import matplotlib.pyplot as plt

i_support = 45.6166667              # Наклонение опорной орбиты, град.
i_target = 0                        # Наклонение ГСО, град.
delta_i = i_support - i_target      # Изменение наклонения орбиты КА, град.
i_p = 0                             # Поворот орбиты в перигее, град.
mu_Earth = 398600                   # Гравитационный параметр Земли, км^3/c^2
R_Earth = 6371                      # Радиус Земли, км
h_p = 300                           # Высота перигея переходной орбиты, км
h_a = 35793                         # Высота апогея переходной орбиты, км
r_p = R_Earth + h_p                 # Радиус переходной орбиты в перигее, км
r_a = R_Earth + h_a                 # Радиус переходной орбиты в апогее, км
m_top = 6550                        # Масса топлива, кг
m_PN = 5000                         # Масса ПН
m_RB = 6650                         # Масса РБ
M_0 = m_RB + m_PN                   # Масса КА (РБ + ПН), кг
I = 333.2 * 9.81/1000               # Удельный импульс, км/с
dict_i_speed = []

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
    return round(sum_V, 7)


def fuel_consumption(M_0):             # Необходимая масса топлива на перелет с минимальной импульсной скоростью
    m_t = M_0 * (1 - math.exp((-min_speed)/I))
    m_t = round(m_t)
    return m_t

m_PG_array = []
m_t_array = []
def search_m_PN(m_t, m_PG):                  # Подбор массы ПН для перелета
    while(m_top < m_t):
        m_PG = m_PG - step
        m_PG_array.append(m_PG)
        M_start = m_RB + m_PG
        m_t = fuel_consumption(M_start)
        m_t_array.append(m_t)
    print('Допустимая масса ПН для перелета с опорной орбиты на ГСО = ', m_PG, '\n Израсходованное топливо РБ составит, кг : ', m_t)


for i in np.arange(i_p, 10 + 0.2, 0.2):    # Нахождение оптимального угла поворота в перигее
    increase_speed_in_per(i)
    increase_speed_in_ap(delta_i, i)
    dict_i_speed.append({'speed': sum_speed(increase_speed_in_per(i), increase_speed_in_ap(delta_i, i)), 'i_p': round(i, 7), 'i_a': round(delta_i - i, 7)})

print('Итерации расчета оптимального угла поворота в перигее переходной орбиты')
for elem in dict_i_speed:
    print(elem)

min_speed = min([x['speed'] for x in dict_i_speed])
print("Минимальная импульсная скорость, необходимая для перелета: ", min_speed)

speed_array = [x['speed'] for x in dict_i_speed]
i_p_array = [x['i_p'] for x in dict_i_speed]


print('Масса топлива для перелета с минимальной скоростью: ', fuel_consumption(M_0))
step = int(input("Задайте шаг уменьшения массы ПН - "))
search_m_PN(fuel_consumption(M_0), m_PN)
1
plt.plot(i_p_array, speed_array)
plt.grid()
plt.show()
plt.plot(m_PG_array, m_t_array)
plt.grid()
plt.show()
