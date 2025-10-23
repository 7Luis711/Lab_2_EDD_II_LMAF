class Airport:
    def __init__(self, code, name, city, country, latitude, longitude):
        self.code = code
        self.name = name
        self.city = city
        self.country = country
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __repr__(self):
        return f"{self.code} - {self.name} ({self.city}, {self.country})"

    def info(self):
        """Devuelve un diccionario con toda la información del aeropuerto"""
        return {
            "Código": self.code,
            "Nombre": self.name,
            "Ciudad": self.city,
            "País": self.country,
            "Latitud": self.latitude,
            "Longitud": self.longitude
        }
