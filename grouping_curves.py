import libs_set as libs

# określenie grupy do której należy dana krzywa
def specifyGroup(SOH):
    # zakresy wartości SOH
    # [(0.95, 1), (0.9, 0.95), (0.8, 0.9), (0.7, 0.8), (0.6, 0.7), (0.5, 0.6), (0.4, 0.5), (0.3, 0.4)]
    if  0.95 < SOH <= 1:
        return 1
    if  0.9 < SOH <= 0.95:
        return 2
    if  0.8 < SOH <= 0.9:
        return 3
    if  0.7 < SOH <= 0.8:
        return 4
    if  0.6 < SOH <= 0.7:
        return 5
    if  0.5 < SOH <= 0.6:
        return 6
    if  0.4 < SOH <= 0.5:
        return 7
    if  0.3 < SOH <= 0.4:
        return 8

def calculate_SOHs(df):
    Cap = []
    for index, row in df.iterrows():
        Cap.append(libs.np.trapz(row['current'], row['relativeTime']) / 3600)
        
    SOH = []
    for elem in Cap:
        SOH.append(elem / Cap[0])
    return SOH    
            
def FitPolynomialsAndRealCurves(df_ref_discharge, polynomial_degree, index_list, draw_graphs=False, show_polynomials=False, create_groups=False):
    
    # znalezienie najlepszego dopasowania do wszystkich krzywych z rodziny, jest to potrzebne do obliczania progu rankingu w modelu ewolucyjnym dla krzywej której przebieg próbujemy przewidzieć
    if not create_groups:
        allSetsOfCoeffs = []
        SetsOfCoeffs = []
        for index, df_row in df_ref_discharge.iterrows():
            coeffs = libs.np.polyfit(df_row['relativeTime'], df_row['voltage'], polynomial_degree)
            allSetsOfCoeffs.append(coeffs)
            if index in index_list:
                df_row = df_ref_discharge.loc[index]
                coeffs = libs.np.polyfit(df_row['relativeTime'], df_row['voltage'], polynomial_degree)
                SetsOfCoeffs.append(coeffs)
                wielomian = libs.np.poly1d(coeffs)
                if show_polynomials is True:
                    print("wielomian " + str(index) + ":\n", wielomian)
                x_model = df_row['relativeTime']  # Zakres wartości x
                y_model = wielomian(x_model)  # Oblicz wartości funkcji wielomianu dla punktów x
            
                # Rysowanie wykresu
                if draw_graphs is True:
                    polyfitModelAndRealCurve(df_row, x_model, y_model)
                    # drawRealCurveAndModel(df_row, x_model, y_model)    
                
        coeffs_grouped = libs.np.array(SetsOfCoeffs).transpose()    
        for group in coeffs_grouped:
            group = group.sort()
            
        coeffs_ranges = []
        for group in coeffs_grouped:
             coeffs_ranges.append( (group.min(), group.max()) )
             #coeffs_ranges.append( (group[: int(len(group) / 2)].mean(), group[int(len(group) / 2) :].mean()) )
        
        return coeffs_ranges, allSetsOfCoeffs, coeffs_grouped
    
    else:
        allSetsOfCoeffs = []
        for index, df_row in df_ref_discharge.iterrows():
            df_row = df_ref_discharge.loc[index]
            coeffs = libs.np.polyfit(df_row['relativeTime'], df_row['voltage'], polynomial_degree) 
            allSetsOfCoeffs.append(coeffs)
            # Rysowanie wykresu
            if draw_graphs == True:
                wielomian = libs.np.poly1d(coeffs)
                x_model = df_row['relativeTime']  # Zakres wartości x
                y_model = wielomian(x_model)  # Oblicz wartości funkcji wielomianu dla punktów x
                polyfitModelAndRealCurve(df_row, x_model, y_model)
        
            
        # pogrupowanie krzywych na 8 grup       
        SOHs = calculate_SOHs(df_ref_discharge)
        
        groups =  [[] for _ in range(8) ]
        for i in index_list:
            df_row = df_ref_discharge.loc[i]
            coeffs = libs.np.polyfit(df_row['relativeTime'], df_row['voltage'], polynomial_degree) 
            curve_grp = specifyGroup(SOHs[i])
            groups[curve_grp-1].append(coeffs)

            
        # stworzenie grup zawierających zakresy współczynników dla kolejnych członów wielomianów, grupy były tworzeone wg przedziału w jakim mieściła
        # się wartość SOH dla aktualnej krzywej
        coeffs_ranges_groups = []
        for elem in groups:
            coeffs_ranges_grp = []
            for i in range(polynomial_degree + 1):
                cff_grp = []
                for setOfCoeffs in elem:
                    cff_grp.append(setOfCoeffs[i])
                cff_range = (libs.np.array(cff_grp).min(), libs.np.array(cff_grp).max())    
                coeffs_ranges_grp.append(cff_range)    
            coeffs_ranges_groups.append(coeffs_ranges_grp)
        
        return coeffs_ranges_groups, SOHs    
    