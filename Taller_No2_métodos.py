import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import SimpleExpSmoothing   
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.seasonal import STL

#primero cargaremos los datos

dtf = pd.read_excel('dtf solo 120 datos.xlsx')
dtf = dtf.rename(columns={'Año(aaaa)-Mes(mm) ': 'Año-Mes'})


#Visualización de los datos

plt.figure(figsize=(14,6))
plt.plot(dtf['Año-Mes'], dtf['DTF'], label='dtf', marker='o', color='b')
plt.title('Serie de tiempo del DTF')
plt.xlabel('Año-Mes')
plt.ylabel('dtf')
plt.xticks(rotation=45)
plt.grid(True) #sirve para ponerle cuadricula a la grafica
plt.tight_layout() 
plt.savefig('dtf.png')


#2.1Pronóstico de los promedios móviles

dtf['Promedio_movil'] = dtf['DTF'].rolling(window=12).mean() 
plt.figure(figsize=(14,6))
plt.plot(dtf['Año-Mes'], dtf['DTF'], label='dtf', marker='o', color='b') 
plt.plot(dtf['Año-Mes'], dtf['Promedio_movil'], label='Promedio móvil', color='r', linestyle='--')
plt.title('Serie de tiempo del DTF y promedio móvil')
plt.xlabel('Año-Mes')
plt.ylabel('dtf')
plt.xticks(rotation=45)
plt.legend(loc='best')
plt.grid(True) 
plt.tight_layout() 
plt.savefig('dtf_promedio_movil.png')


#2.2Pronóstico de suavización exponencial simple

months_str = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

dtf['Suavizacion_exp_simple'] = SimpleExpSmoothing(dtf['DTF']).fit(smoothing_level=0.2, optimized=False).fittedvalues.shift(-1) #fittedvalues sirve para obtener los valores ajustados
plt.figure(figsize=(14,6))
plt.plot(dtf['Año-Mes'], dtf['DTF'], label='dtf', marker='o', color='b')
plt.plot(dtf['Año-Mes'], dtf['Suavizacion_exp_simple'], label='Suavización exponencial simple', color='g', linestyle='--')
plt.title('Serie de tiempo del DTF y suavización exponencial simple')
plt.xlabel('Año-Mes')
plt.ylabel('dtf')
plt.xticks(rotation=45)
plt.legend(loc='best')
plt.grid(True)
plt.tight_layout()
plt.savefig('dtf_suavizacion_exp_simple.png')


#2.3 Modelo Pronóstico de Indices estacionales

stl = STL(dtf['DTF'], seasonal=13, period=12) #dividimos el periodo en 13 meses
res = stl.fit()

dtf['Tendencia'] = res.trend
dtf['Estacionalidad'] = res.seasonal
dtf['Residuales'] = res.resid

Pronostico = [dtf['Tendencia'].iloc[-1] + dtf['Estacionalidad'].iloc[-1] for i in range(12)]

plt.figure(figsize=(14,6))
plt.bar(months_str, Pronostico, color='coral')
plt.title('Pronóstico de Indices estacionales')
plt.xlabel('Año-Mes')
plt.ylabel('dtf')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('dtf_indices_estacionales.png')



#2.4 Regresiones polinómicas

X = np.arange(len(dtf)).reshape(-1,1)
y = dtf['DTF'].values
lin_reg = LinearRegression().fit(X, y)
dtf['Linear_Trend'] = lin_reg.predict(X)
poly2 = PolynomialFeatures(degree=2)
X_poly2 = poly2.fit_transform(X)
lin_reg2 = LinearRegression().fit(X_poly2, y)
dtf['Poly2_Trend'] = lin_reg2.predict(X_poly2)
poly3 = PolynomialFeatures(degree=3)
X_poly3 = poly3.fit_transform(X)
lin_reg3 = LinearRegression().fit(X_poly3, y)
dtf['Poly3_Trend'] = lin_reg3.predict(X_poly3)
plt.figure(figsize=(14, 6))
plt.plot(dtf['Año-Mes'], dtf['DTF'], label='DTF Original', marker='o', color='b')
plt.plot(dtf['Año-Mes'], dtf['Linear_Trend'], label='Tendencia Lineal', color='r', linestyle='--')
plt.plot(dtf['Año-Mes'], dtf['Poly2_Trend'], label='Polinomio Grado 2', color='g', linestyle='-.')
plt.plot(dtf['Año-Mes'], dtf['Poly3_Trend'], label='Polinomio Grado 3', color='purple', linestyle=':')
plt.title('Serie de tiempo de DTF de Colombia y Regresiones Polinómicas')
plt.xlabel('Fecha (Año-Mes)')
plt.ylabel('DTF')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('regresiones_polinomicas.png')

#Correlacion
correlacion = dtf['DTF'].corr(pd.Series(np.arange(len(dtf))))
print(correlacion)

# 3. Medidas de error de pronóstico
def mean_absolute_percentage_error(y_true, y_pred): 
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

models = ['Promedio_movil', 'Suavizacion_exp_simple', 'Linear_Trend', 'Poly2_Trend', 'Poly3_Trend']
errors = {'Model': [], 'MSE': [], 'MAE': [], 'MAPE': []}
for model in models:
    y_pred = dtf[model].dropna()
    y_true = dtf['DTF'].iloc[y_pred.index]
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    errors['Model'].append(model)
    errors['MSE'].append(mse)
    errors['MAE'].append(mae)
    errors['MAPE'].append(mape)
error_df = pd.DataFrame(errors)

error_df


def save_df_as_image(df, filename):
    fig, ax = plt.subplots(figsize=(10, 4)) # ajusta el tamaño según prefieras
    ax.axis('off') # desactiva los ejes
    ax.table(cellText=df.values,
             colLabels=df.columns,
             cellLoc = 'center', 
             loc='center',
             bbox=[0, 0, 1, 1])
    plt.savefig(filename)

# Guardar el DataFrame de errores como imagen
save_df_as_image(error_df, 'errores.png')

























