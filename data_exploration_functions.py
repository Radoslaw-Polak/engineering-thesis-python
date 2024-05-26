import libs_set as libs


def mat_to_dataframe(file_path):
    # Load the .mat file
    mat_data = libs.loadmat(file_path)
    # Extract the 'data' structure
    data = mat_data['data']

    # Create a dictionary to store extracted data
    extracted_data = {}

    # Extract fields
    extracted_data['procedure'] = data['procedure'][0][0]
    extracted_data['description'] = data['description'][0][0]

    # Extract step data into a dataframe
    step_data = data['step'][0][0]
    df_steps = libs.pd.DataFrame()
    
    comments = []
    types = []
    relative_times = []
    times = []
    voltages = []
    currents = []
    temperatures = []
    dates = []

    for i in range(step_data.size):
        comments.append(step_data['comment'][0][i][0])
        types.append(step_data['type'][0][i][0])
        relative_times.append(step_data['relativeTime'][0][i][0])
        times.append(step_data['time'][0][i][0])
        voltages.append(step_data['voltage'][0][i][0])
        currents.append(step_data['current'][0][i][0])
        temperatures.append(step_data['temperature'][0][i][0])
        dates.append(step_data['date'][0][i][0])
    
    df = libs.pd.DataFrame(zip(comments, types, relative_times, times, voltages, currents, temperatures, dates),
                          columns = ['comment', 'type', 'relativeTime', 'time', 'voltage', 'current', 'temperature', 'date'])
    
    # df.set_index('comment', inplace = True)

    return extracted_data, df

def df_filtered(comment, df_rwX):
    filt = df_rwX['comment'] == comment
    df = df_rwX.where(filt).dropna() 
    return df

def drawSingleCurve(df_row, linewidth):
    libs.plt.figure(figsize=(8 ,4))
    libs.plt.plot(df_row['relativeTime'], df_row['voltage'], color='black', linewidth = linewidth)
    libs.plt.xlabel('time [h]')
    libs.plt.ylabel('voltage [V]')
    libs.plt.show()

def drawCurves(df, linewidth_vol, linewidth_cur, linewidth_temp):
    
    # krzywe napięcia od czasu
    libs.plt.figure(figsize=(8 ,4))
    for index, row in df.iterrows():
         libs.plt.plot(row['relativeTime'], row['voltage'], color='black', linewidth = linewidth_vol)
         
    libs.plt.xlabel('time [s]')
    libs.plt.ylabel('voltage [V]')
    libs.plt.show()
    
    # krzywe natężenia od czasu
    libs.plt.figure(figsize=(8, 4))
    for index, row in df.iterrows():
         libs.plt.plot(row['relativeTime'] / 3600 , row['current'], color='black', linewidth = linewidth_cur)
         
    libs.plt.xlabel('time [h]')
    libs.plt.ylabel('current [A]')
    libs.plt.show()
    
    # krzywe temperatury od czasu
    libs.plt.figure(figsize=(8, 4))
    for index, row in df.iterrows():
         libs.plt.plot(row['relativeTime'] / 3600 , row['temperature'], color='black', linewidth = linewidth_temp)
         
    libs.plt.xlabel('time [h]')
    libs.plt.ylabel('temperature [°C]')
    libs.plt.show()
    
def polyfitModelAndRealCurve(df_row, x_model, y_model):
    libs.plt.figure()
    libs.plt.plot(df_row['relativeTime'], df_row['voltage'], color='k')
    libsplt.plot(x_model, y_model, color='b')
    libs.plt.xlabel('time [s]')
    libs.plt.ylabel('voltage [V]')
    libs.plt.show()
    
def drawRealCurveAndModel(polynomial_degree, curve_index, df_row, x_model, y_model, x_prediction_start=None, y_prediction_start=None):
    # rysowanie funkcji stałej napięcia krytycznego
    crit_voltage = 3.2
    x = libs.np.linspace(0, 10000, 10)
    y = crit_voltage * libs.np.ones(len(x))
    
    libs.plt.figure()  # Tworzenie nowego wykresu
    # zaznaczenie punktu rozpoczęcia predykcji
    libs.plt.plot(df_row['relativeTime'], df_row['voltage'], label='Krzywa rzeczywista', color='black')
    libs.plt.plot(x_model, y_model, label='Model', color='green')
    libs.plt.plot(x, y, label="Napięcie krytyczne (rozładowania)", color='blue', linestyle='--')
    if (x_prediction_start and y_prediction_start) != None: 
        libs.plt.plot(x_prediction_start, y_prediction_start, label='Punkt rozpoczęcia predykcji', marker='v', color='red')
    libs.plt.xlim([0, max(df_row['relativeTime']) + 1500])
    libs.plt.ylim([3, 4.5])
    libs.plt.xlabel('time [s]')
    libs.plt.ylabel('voltage [V]')
    libs.plt.legend()
    libs.plt.title(f'Model: wielomian {polynomial_degree} stopnia \n Krzywa {curve_index}')
    # Wyświetlenie wykresu

    
def drawFunction(x, y, label, xlabel, ylabel, title):
    libs.plt.plot(x, y, label=label)
    libs.plt.plot(x[-1], y[-1], color='k', marker='o')
    libs.plt.plot([x[-1], x[-1]], [0, y[-1]], linestyle='--', color='k')
    libs.plt.xlabel(xlabel)
    libs.plt.ylabel(ylabel)
    libs.plt.title(title)
    libs.plt.legend()
    
    
def MeasuredCapacity(df, n_curves):
    df['date'] = libs.pd.to_datetime(df['date'])

    # Zapis daty i pojemności dla cykli referencyjnych rozładowania
    Cap = []
    for index, row in df.iterrows():
        Cap.append(libs.np.trapz(row['current'], row['relativeTime']) / 3600)
    
    # Określenie zakresu dat dla wykresu
    ExpStart = df['date'].min()
    ExpEnd = df['date'].max()
    
    # Inicjalizacja wykresu
    libs.plt.xlim([ExpStart, ExpEnd])
    libs.plt.plot(df['date'], Cap, 'ko')
    libs.plt.xlabel('date')
    libs.plt.xticks(rotation = 45)
    libs.plt.ylabel('Measured Capacity (Ah)')
    
    libs.plt.show()
    print(len(Cap))
    
    # Zależność pojemności od liczby cykli
    # jest n krzywych rozładowywania i ładowania a każda kolejna krzywa odpowiada stanowi po 50 cyklach RW (random walk) 
    cycles = range(0, 50*n_curves, 50)
    
    # wykres zależności pojemności od liczby cykli
    libs.plt.plot(cycles, Cap, 'ro')
    libs.plt.xlabel('liczba cykli')
    libs.plt.ylabel('Mierzona pojemność [Ah]')
    libs.plt.show()
    
    libs.plt.plot(cycles, (Cap / Cap[0]) * 100, 'bo')
    libs.plt.xlabel('liczba cykli')
    libs.plt.ylabel('SOH')
    libs.plt.show()
    
    return cycles, Cap    

def determineIndexForTestBattery(test_battery_df, curve_index, n_curves_test_battery):
    df_row = None
    possible_curve_index = curve_index
    if curve_index > n_curves_test_battery - 1:
        df_row = test_battery_df.loc[n_curves_test_battery-1]
        possible_curve_index = n_curves_test_battery - 1
    else:    
        df_row = test_battery_df.loc[curve_index]
    return df_row, possible_curve_index    
