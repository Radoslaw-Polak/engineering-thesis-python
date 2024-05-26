import libs_set as libs

# funkcja realizująca genetyczne dobieranie współczynników wielomianu
def EvolutionaryModel(time_full, voltage_full, time_part, voltage_part, coeffs_ranges, best_fit_coeffs, coeffs_ranges_groups, curve_group,
                                                                  grouping_profiles=True,
                                                                  n_pop=1000,
                                                                  n_gens=1000, 
                                                                  n_best=100, 
                                                                  mutation_rate=0.02,
                                                                  mutation_with_prob=False,
                                                                  crossover=False,
                                                                  random_crossover_point=True,
                                                                  limit_rank_threshold=1,
                                                                  modify_n_best=False,
                                                                  min_gens_to_complete=5,
                                                                  avgBestCoeffs = False,
                                                                  n_best_best = 10):
   
    # funkcja do obliczenia błędu średniokwadratowego
    def calculate_mse(time, voltage, cff_individual):       
        model_polynomial = libs.np.poly1d(cff_individual)
        model_values = model_polynomial(time)
        mse = ((voltage - model_values) ** 2).mean()
        return mse
    
    # --------------------------
    # Funkcje dokonujące mutacji
    #---------------------------
    
    # mutacja dokonywana na konkretnej wartości (konkretnym współczynniku)
    def mutate(value, percentage_diff):
        return value * libs.random.uniform(1 - percentage_diff, 1 + percentage_diff)
    
    # mutacja dokonywana na danym osobniku (zestawie współczynników)
    def mutation(cff_individual, mutation_rate):
        # draw_index = random.randint( 0, len(cff_individual) - 1 )
        new_cff_individual = []
        for cff in cff_individual:
            cff = mutate(cff, mutation_rate)
            new_cff_individual.append(cff)
        return new_cff_individual    
    
    # krzyżowanie dla pojedyńczej pary osobników
    def crossover(parent1, parent2, random_crossover_point=True):
        crossover_point = 0
        if random_crossover_point:
            crossover_point = libs.np.random.randint(1, len(parent1))
        else:
            crossover_point = int(len(parent1) / 2)
        child1 = libs.np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = libs.np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
        return list(child1), list(child2)
        
    # operacja krzyżowania na osobnikach całej generacji (crossoveredGeneration)
    def crossoverOperation(crossoveredGeneration, random_crossover_point):
        # Wybór par do krzyżowania bez powtórzeń
        individuals_indices = list(range( len(crossoveredGeneration) ))
        # libs.random.shuffle(individuals_indices)
        pairs_indices = [individuals_indices[i:i+2] for i in range(0, len(individuals_indices), 2)]

        # Dokonanie krzyżowania na osobnikach z aktualnej populacji
        for pair_indices in pairs_indices:
            parent1 = crossoveredGeneration[pair_indices[0]]
            parent2 = crossoveredGeneration[pair_indices[1]]
            child1, child2 = crossover(parent1, parent2, random_crossover_point)
            crossoveredGeneration[pair_indices[0]] = child1
            crossoveredGeneration[pair_indices[1]] = child2    
        return crossoveredGeneration
    
    def determineIfTheFunctionIsDecreasing(time_interval, coeffs):
        current_model = libs.np.poly1d(coeffs)
        derivative = current_model.deriv()
        isDecreasingFunction = libs.np.all( derivative(time_interval) < 0)
        return isDecreasingFunction
    

    def avgNbestCoeffs(N, aux_ranked_individuals):
        
        aux_ranked_individuals = libs.np.array(aux_ranked_individuals, dtype=[('rank', float), ('coeffs', object), ('prob', float)])
        sorted_indexes = libs.np.argsort( aux_ranked_individuals[:]['rank'] )
        n_max_indexes = sorted_indexes[-N:]
        best_ranked_individuals = aux_ranked_individuals[n_max_indexes]
        
        ranks = libs.np.array([elem[0] for elem in best_ranked_individuals])
        best_coeffs_sets = libs.np.array([elem[1] for elem in best_ranked_individuals])
        
        avg_rank = ranks.mean()
        
        best_sets_grouped = best_coeffs_sets.transpose()
        optimal_coeffs = []
        for group in best_sets_grouped:
            optimal_coeffs.append(group.mean())
         
        return avg_rank, optimal_coeffs
        
    print("Genetic model")
    # inicjacja populacji
    if grouping_profiles is False:
        print("ZWYCZAJNA INICJACJA POPULACJI")
        coefficient_individuals = [] # lista osobników (zestawów współczynników wielomianu)
        for _ in range(n_pop):
             coeffs_set = []
             for cff_range in coeffs_ranges:
                 coeffs_set.append( libs.random.uniform(cff_range[0], cff_range[1]) )       
             coefficient_individuals.append(coeffs_set)
    else:
        # inicjacja populacji wg wyznaczonych grup zakresów współczynników
        # print("Kolejne osobniki, bez wykonywania random.shuffle")
        coefficient_individuals = [] # lista osobników (zestawów współczynników wielomianu)
        for _ in range(n_pop):
            coeffs_set = []
            # przechodzimy po zakresach współczynników przy kolejnych członach wielomianu dla grupy do której należy analizowana krzywa
            for cff_range in coeffs_ranges_groups[curve_group-1]: 
                coeffs_set.append( libs.random.uniform(cff_range[0], cff_range[1]) )       
            coefficient_individuals.append(coeffs_set)    
    
    mse_list = [] # lista błędów list błędów średniokwadratowych
    n = 0 # licznik generacji
    mse_limit = calculate_mse(time_full, voltage_full, best_fit_coeffs)
    rank_limit = 1 / mse_limit
    print("Rank limit: ", rank_limit)
    
    # ewolucja 
    aux_ranked_individuals = []
    for generation in range(n_gens):
        n += 1
        ranked_individuals = []
        for cff_individual in coefficient_individuals:
            mse = calculate_mse(time_part, voltage_part, cff_individual)
            rank = 1 / mse
            #coeffs_mse = mean_squared_error(cff_individual, best_fit_coeffs)
            # coeffs_rank = 1 / coeffs_mse
            time_interval = libs.np.arange(time_part[-1] - 100, time_full[-1], 10) 
            isDecreasingFunction = determineIfTheFunctionIsDecreasing(time_interval, cff_individual)
            ranked_individuals.append( (rank, cff_individual, 1 - rank / rank_limit, isDecreasingFunction) )
            # mutation(time, voltage, cff_individual, ranked_individuals, 0.01)
        ranked_individuals = sorted(ranked_individuals, key=lambda x: x[0], reverse=True)
                     
        #print(f"\n=== GEN: {generation} best solution ===")
        print(f'Ranking  najlepszego: {ranked_individuals[0][0]}')
        mse_list.append(1/ranked_individuals[0][0])
        mse_array = libs.np.array(mse_list)
        
        aux_ranked_individuals.append(ranked_individuals[0])
        
        # pochodna dla aktualnego modelu wielomianu (określenie czy funkcja jest malejąca na przedziale od punktu rozpoczęcia predykcji do ostatniej zmierzonej chwili czasu)
        time_interval = libs.np.arange(time_part[-1] - 100, time_full[-1] + 100, 10) 
        isDecreasingFunction = determineIfTheFunctionIsDecreasing(time_interval, ranked_individuals[0][1])
        
        if n == 0.25 * n_gens: # and ranked_individuals[0][0] < rank_limit * limit_rank_threshold:
            limit_rank_threshold -= 0.1
            print(f'Zmniejszono próg rankingu do {limit_rank_threshold * 100} %')
        if n == 0.5 * n_gens: # and ranked_individuals[0][0] < rank_limit * limit_rank_threshold:
            limit_rank_threshold -= 0.1
            print(f'Zmniejszono próg rankingu do {limit_rank_threshold * 100} %')
        
        # warunek końca 
        if ranked_individuals[0][0] > rank_limit * limit_rank_threshold and n >= min_gens_to_complete and isDecreasingFunction:
           print(f"PRÓG RANKINGU OGRANICZONY DO {limit_rank_threshold*100} %")
           if avgBestCoeffs == False:
               print("Osobnik o najwyższym rankingu:")
               # print(ranked_individuals[0][1])
               return ranked_individuals[0][0], ranked_individuals[0][1] , mse_list, n
           else:
               if n < n_best_best:
                   n_best_best = n
               print(f"\nUśrednienie {n_best_best} najlepszych osobników ze zrealizowanych generacji:")    
               avg_rank, optimal_coeffs = avgNbestCoeffs(n_best_best, aux_ranked_individuals)
               return avg_rank, optimal_coeffs, mse_list, n

        # selekcja najlepszych osobników z danej generacji i zapisanie ich do listy wraz z odpowiadającymi im rankingami
        ranked_best_individuals = ranked_individuals[:n_best]
        
        # mutacja
        newGeneration = []
        
        # Czy dokonujemy operacji genetycznych (mutacja i krzyżowanie) na najlepszych osobnikach z danej generacji ? Domyślnie nie, najlepsze osobniki przechodzą do następnej generacji bez zmian. 
        iter = n_pop - n_best
        if modify_n_best:
            iter = n_pop
            
        if mutation_with_prob:
            # zapisanie najlepszych osobników do listy *(zestawy współczynników i prawdopodobieństwo mutacji)
            # zapisanie do nowej generacji najlepszych osobników z ostatniej generacji a następnie wygenerowanie na ich podstawie nowych osobników
            # aby dopełnić liczność nowej genracji do liczności populacji
            best_individuals = []
            for rbi in ranked_best_individuals:
                best_individuals.append( (rbi[1], rbi[2]) )
                if not modify_n_best:
                    newGeneration.append( rbi[1] )
    
            # mutacja (na podstawie prawdopodobieństwa mutacji)
            # newGeneration = []   
            for _ in range(iter):
                # Tutaj usunąłem warunek z prawdopodobieństwem, po prostu każdy osobnik jest poddawany mutacji
                # coeffs_set = [] 
                rand_best_ind = libs.random.choice(best_individuals)
                mutated_ind = rand_best_ind[0]

                if libs.random.random() <= rand_best_ind[1]: # and isDecreasingFunction:                    
                    mutated_ind = mutation(mutated_ind, mutation_rate)
                newGeneration.append( (mutated_ind) ) 
        
        else:
            best_individuals = []
            # zapisanie najlepszych osobników do listy (same zestawy współczynników, nie uwzględniamy prawdopodobieństwa mutacji)
            # zapisanie do nowej generacji najlepszych osobników z ostatniej generacji a następnie wygenerowanie na ich podstawie nowych osobników
            # aby dopełnić liczność nowej genracji do liczności populacji
            for rbi in ranked_best_individuals:
                best_individuals.append( rbi[1] )
                if not modify_n_best:
                    newGeneration.append( rbi[1] )
                
            # pogrupowanie współczynników według tego przy członach którego stopnia wielomianu się znajdują
            best_individuals_grouped = libs.np.array(best_individuals).transpose()        
     
            for _ in range(iter):
              #coeffs_set = [] 
              rand_best_ind = libs.random.choice(best_individuals)  
              mutated_ind = rand_best_ind
              mutated_ind = mutation(mutated_ind, mutation_rate)
              newGeneration.append(mutated_ind)  
              #for cff_group in best_individuals_grouped:
                  #if index % mutation_freq == 0:                   
              #    coeffs_set.append( mutate( libs.random.choice(cff_group), mutation_rate ) )
                  # else:
                  #     coeffs_set.append( libs.random.choice(cff_group) )
              #newGeneration.append(coeffs_set)                       
        
    
        # Krzyżowanie dokonywane na populacji z listy newGeneration (przetestować może takie krzyżowanie ze zawsze będzie względem tego samego punktu, że za każdym rzem
        # połowa współczynników potomka będzie z 1 rodzica a druga połowa z 2 rodzica i na odwrót dla 2 potomka
        # print("Krzyżowanie tylko na nowo wygenerowanych osobnikach (nie na najlepszych wybranych)")
        if crossover:
            # krzyżowanie wykonane na nowo wygenerowanych osobnikach (n_best najlepszych osobników z danej generacji nie jest poddawane operacjom genetycznym mutacji i selekcji)
            if not modify_n_best:
                newGeneration[n_best:] = crossoverOperation(newGeneration[n_best:], random_crossover_point)
            else:
                newGeneration = crossoverOperation(newGeneration, random_crossover_point)

        # aktualizacja populacji
        coefficient_individuals = newGeneration
        
    # jeśli ewolucja nie została przerwana podczas działania pętli (nie została przekroczona dana wartość rankingu) to wyszukujemy osobnika
    # o najwyższym rankingu
    if avgBestCoeffs == False:
        print("Osobnik o najwyższym rankingu:")
        # print(ranked_individuals[0][1])
        max_rank_individual = max(aux_ranked_individuals, key=lambda x: x[0])
        return max_rank_individual[0], max_rank_individual[1], mse_list, n
    else:
        if n < n_best_best:
            n_best_best = n
        print(f"\nUśrednienie {n_best_best} najlepszych osobników ze zrealizowanych generacji:")  
        avg_rank, optimal_coeffs = avgNbestCoeffs(n_best_best, aux_ranked_individuals)
        return avg_rank, optimal_coeffs, mse_list, n