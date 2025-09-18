#No AI Prac

class Cars:
    def __init__(self, car_name: str, brand: str, milleage: int):
        self.car_name = car_name
        self.brand = brand
        self.milleage = milleage

    def calculation(self):
        random_calc = self.milleage*10
        return random_calc
    
    def lifetime_fuel_cost(self, fuel_cost: int):
        calc = fuel_cost*self.milleage
        return calc
    
    def car_info(self):
        print('Car Name:', self.car_name , 'Car Brand:', self.brand, 'Car Milleage:', self.milleage)
    


car_1 = Cars('Civic', 'Honda', 10)
car_2 = Cars('Dart', 'Dodge', 100)      

fuel = car_1.lifetime_fuel_cost(20)
print(fuel)

