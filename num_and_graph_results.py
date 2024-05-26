import libs_set as libs

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
    libs.plt.xlabel('czas [s]')
    libs.plt.ylabel('Napięcie podczas rozładowywania baterii [V]')
    libs.plt.legend(loc='upper right')
    libs.plt.title(f'Model: wielomian {polynomial_degree} stopnia \n Krzywa {curve_index}')

 
# znalezienie czasu pozostałego do rozładowania baterii, funkcja rozwiązująca równanie (znalezienie punktu przecięcia krzywej z krytycznym poziomem napięcia)
def findRemainingTime(optimal_coeffs, time_full, time_partial, return_values_only=False):
 
    equation_coeffs = optimal_coeffs.copy()
    equation_coeffs[-1] = equation_coeffs[-1] - 3.2
 
    model = libs.np.poly1d(equation_coeffs)
    roots = libs.np.roots(model)
    
    real_time = time_full[-1] - time_partial[-1]
    real_roots = roots[roots.imag == 0].real
    positive_real_roots = real_roots[real_roots > 0]
    if libs.np.size(positive_real_roots):
        is_solution = True
        abs_diffs = (positive_real_roots - time_full[-1])
        min_abs_diff = abs_diffs.min() # najmniejsza różnica między rzeczywistym pierwiastkiem a ostatnim pomiarem czasu dla 
        # testowanej krzywej
        my_root = positive_real_roots[libs.np.where(abs_diffs == min_abs_diff)] # znalezienie pierwiastka dla minimalnej różnicy z parametrem time[-1]
        estimated_time = abs(my_root - time_partial[-1])
        abs_error = abs(real_time-estimated_time)
        rel_error = abs(real_time-estimated_time) / real_time
        if return_values_only:          
            return estimated_time, real_time, abs_error, rel_error, is_solution
        else:
            print("Rozwiązania:")
            for root in roots:
                print(root)
            print("Rozwiązanie równania wielomianowego: ", my_root)
            print("Rzeczywista chwila czasu (na podstawie danych pomiarowych): ", time_full[-1])
            
            return estimated_time, real_time, abs_error, rel_error, is_solution
            
    else:
        is_solution = False
        print("Nie było rozwiązania rzeczywistego !")
        return None, real_time, None, None, is_solution

    
# dodana funkcja do wyświetlania wyników cząstkowych lub uśrednionych:
# cząstkowe - czyli dla konkretnej krzywej (po przejściu przez n iteracji)
# uśrednione - czyli po przejściu przez wszystkie krzywe, uzyskanie wszystkich wyników cząstkowych i obliczenie wyników końcowych (uśrednionych) poprzez uśrednienie błędów względnych, bezwzględnych oraz dokładności z każdego wyniku cząstkowego, są to wyniki odnoszące się do ogólnej oceny działania modelu 
# i dla 2 metod wyznaczania czasu:
# na podstawie uśredniania krzywych - czyli w każdej iteracji dla danej krzywej liczymy szacowany czas a następnie uśredniamy go i mamy estymowany czas dla danej krzywej
# na podstawie uśredniania współczynników wielomianu - czyli bierzemy optymalne współczynniki dla danej krzywej z każdej iteracji i uśredniamy je (czyli bierzemy wszystkie współczynniki przy danym  członie wielomianu i je uśredniamy, robimy tak dla współczynnika przy każdym kolejnym członie danego wielomianu)

def printResults(avgd_curves_or_coeffs = 'coeffs', avgd_or_partial_results = 'part', est_time=None, real_time=None, rel_error=None, abs_error=None, avg_rel_error=None, avg_abs_error=None):
    if avgd_curves_or_coeffs == "coeffs":
        print("------Wyniki na podstawie uśrednienia WSPÓŁCZYNNIKÓW WIELOMIANU z kolejnych iteracji dla danej krzywej------")
    elif avgd_curves_or_coeffs == "curves":
        print("------Wyniki na podstawie uśrednienia KRZYWYCH z kolejnych iteracji dla danej krzywej------")
    else:
        print("Możliwe wartości parametrów to 'coeffs' lub 'curves'")
        
    if avgd_or_partial_results == 'part':
        print("Oszacowany czas pozostały do rozładowania: ", est_time)
        print("Rzeczywisty czas pozostały do rozładowania: ", real_time) 
        print(f"Błąd względny: {rel_error * 100} %")
        print(f"Błąd bezwględny: {abs_error} s")
        print(f"Dokładność: { (1-rel_error) * 100} %")
    elif avgd_or_partial_results == 'avg':
        print(f"Średni błąd względny: {avg_rel_error * 100} %")
        print(f"Średni błąd bezwględny: {avg_abs_error} s")
        print(f"Średnia dokładność: { (1-avg_rel_error) * 100} %")
    else:
        print("Możliwe wartości parametrów to 'part' lub 'avg'")
        
    

    
    
    
    