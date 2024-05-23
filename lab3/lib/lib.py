class Vehicle:
  """
  A base class representing a generic vehicle.
  """
  def __init__(self, make, model, year):
    self.make = make
    self.model = model
    self.year = year
    self.wheels = 0

  def start(self):
    """
    Simulates starting the vehicle.
    """
    print(f"The {self.year} {self.make} {self.model} roars to life!")

  def stop(self):
    """
    Simulates stopping the vehicle.
    """
    print(f"The {self.year} {self.make} {self.model} comes to a stop.")

  def get_info(self):
    """
    Returns information about the vehicle.
    """
    return f"{self.year} {self.make} {self.model}"


class Car(Vehicle):
  """
  A subclass of Vehicle representing a car.
  """

  def __init__(self, make, model, year, num_doors):
    super().__init__(make, model, year)
    self.num_doors = num_doors
    self.__key = 2232
    self.wheels = 4

  def honk_horn(self):
    """
    Simulates honking the car horn.
    """
    print(f"The {self.year} {self.make} {self.model} honks its horn (Beep Beep!)")


class Motorcycle(Vehicle):
  """
  A subclass of Vehicle representing a motorcycle.
  """

  def __init__(self, make, model, year, engine_size):
    super().__init__(make, model, year)
    self.engine_size = engine_size
    self.wheels = 2

  def rev_engine(self):
    """
    Simulates revving the motorcycle engine.
    """
    print(f"The {self.year} {self.make} {self.model} engine revs loudly!")

