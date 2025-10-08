import pandas as pd
import matplotlib.pyplot as plt
# ====== Leemos el archivo CaudalesMediosDiarios.csv y calculamos el año hidrológico tipo ======
df_ancho = pd.read_csv("CaudalesMediosDiarios.csv", usecols=range(1,15), sep=";", na_values=["-", "."], decimal=",")
df_largo = df_ancho.melt(id_vars=["Año", "Día"], var_name="Mes", value_name="Caudal")
orden = ["Oct","Nov","Dic","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep"]
df_largo["Mes"] = pd.Categorical(df_largo["Mes"], categories=orden, ordered=True)
Año_tipo_largo=df_largo.groupby(["Día", "Mes"], observed=False)["Caudal"].mean()
Año_tipo_ancho = Año_tipo_largo.unstack(level="Mes")
Año_tipo_ancho = Año_tipo_ancho.round(2) 
Año_tipo_ancho.to_csv("Añotipo.csv")
#====== Leemos el archivo CaudalesMediosAnuales.csv y calculamos el caudal medio anual ======
QMedioAnual = pd.read_csv("CaudalesMediosAnuales.csv", sep=";", decimal=",", usecols=range(1, 3), na_values=["-", "."])
Q_medio_anual=QMedioAnual["Caudal m3/s"].mean().round(2)
print("El caudal medio anual es: ", Q_medio_anual)
# ====== Calculamos el caudal ecológico ======
#20% del caudal medio anual del río en los meses de diciembre, enero y febrero
Qeco20= 0.2*Q_medio_anual #diciembre, enero y febrero
#10% del caudal medio anual resto de meses
Qeco10= 0.1*Q_medio_anual
# ====== Calculamos el año tipo restando el caudal ecológico ======
meses20 =  ["Ene","Feb","Dic"]
meses10 = ["Mar","Abr","May","Jun","Jul","Ago","Sep", "Oct","Nov"]
for i in meses20:
    Año_tipo_ancho[i] = Año_tipo_ancho[i] - Qeco20
for i in meses10:
    Año_tipo_ancho[i] = Año_tipo_ancho[i] - Qeco10
Año_tipo_ancho=Año_tipo_ancho.round(1)
Año_tipo_ancho.to_csv("Añotipo_sin_Qeco.csv")
# ====== Ordenamos de menor a mayor los caudales del año tipo restando el caudal ecológico ======
Año_tipo_ancho = Año_tipo_ancho.reset_index()
Año_tipo_largo = Año_tipo_ancho.melt(id_vars=["Día"], var_name="Mes", value_name="Caudal")
Año_tipo_largo = Año_tipo_largo.sort_values(by="Caudal", ascending=True)
Año_tipo_largo.to_csv("Año_tipo_sin_Qeco_ordenado.csv")
# ====== Calculamos la tabla grande para hacer la gráfica ======
Año_tipo_largo = Año_tipo_largo[~((Año_tipo_largo['Día'] == 29) & (Año_tipo_largo['Mes'] == 'Feb'))] #Eliminamos el 29 de febrero
tabla = (
    Año_tipo_largo.groupby("Caudal")
    .size()
    .reset_index(name="Frecuencia")
    .sort_values(by="Caudal")
    .reset_index(drop=True)
)
tabla["horas"]=tabla["Frecuencia"]*24
tabla["fr(%)"]=tabla["Frecuencia"]/365
tabla["fr(%)"]=tabla["fr(%)"].round(4)
tabla["F"] =tabla["fr(%)"].cumsum().round(4)
tabla["F'"]=1-tabla["F"]
tabla["F'"]=tabla["F'"].round(4)
tabla["Días acumulados"]=tabla["F'"]*365
tabla["Días acumulados"]=tabla["Días acumulados"].round(0)
#Calculamos el salto neto
Hb=30 #Dato del problema
Hp =10 #10% de pérdidas de carga respecto al salto bruto
Hp = Hb*Hp/100
Hn=Hb-Hp
#print("El salto neto es: ", Hn)
tabla["Pth"] = 9.81 * Hn * tabla["Caudal"]
tabla["Pth"] = tabla["Pth"].round(1)
tabla["Eth"] = tabla["Pth"] * tabla["horas"]
tabla["Eth"] = tabla["Eth"].round(1)
#Escogemos como caudal de equipamiento el caudal que más días se repita
#dentro del rango de caudales que son superados entre 80 y 100 días del año
df_filtrado = tabla[(tabla["Días acumulados"] >= 80) & (tabla["Días acumulados"] <= 100)]
Q_equipamiento = df_filtrado.loc[df_filtrado["Frecuencia"].idxmax(), "Caudal"]
print(Q_equipamiento)
#print(tabla)
tabla.to_csv("tabla.csv")
#Realizamos las gráficas
fig, ax = plt.subplots(2, 1, constrained_layout=True)
ax[0].plot(tabla["Caudal"], tabla["Eth"], marker = "o", markersize=2, color="tomato")
ax[0].set_title("Curva de energía hidraulica en función del caudal", fontweight='bold')
ax[0].set_ylabel("Energía (kWh)")
ax[0].set_xlabel("Caudal")
ax[0].grid()
ax[1].plot(tabla["Días acumulados"], tabla["Caudal"], marker = "o", markersize=2)
ax[1].set_ylabel("Caudal")
ax[1].set_title(" Curva de caudales medios clasificados", fontweight='bold')
ax[1].set_xlabel("Días acumulados")
ax[1].grid()
plt.show()

































