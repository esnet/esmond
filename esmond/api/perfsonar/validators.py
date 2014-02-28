import json

'''
DataValidator: Base validator class. Subclasses should override vaildate class
'''
class DataValidator(object):
    def validate(self, value):
        return

'''
FloatValidator: Simple validator for floating point numbers
'''
class FloatValidator(DataValidator):
    def validate(self, value):
        try:
            float(value)
        except ValueError:
            raise BadRequest("Value must be a floating point number")

'''
HistogramValidator: Validator for histogram type
'''
class HistogramValidator(DataValidator):
    def validate(self, value):
        try:
            json.loads(value)
            for k in value:
                long(value[k])
        except ValueError:
            raise BadRequest("Value of histogram must be an integer")
        except:
            raise BadRequest("Invalid histogram provided")

'''
IntegerValidator: Simple validator for integers
'''
class IntegerValidator(DataValidator):
    def validate(self, value):
        try:
            long(value)
        except ValueError:
            raise BadRequest("Value must be an integer")

'''
JSONValidator: Simple validator for json strings
'''
class JSONValidator(DataValidator):
    def validate(self, value):
        try:
            json.loads(value)
        except:
            raise BadRequest("Value must be valid JSON")
        
'''
PercentageValidator: Simple validator for percentage types
'''
class PercentageValidator(DataValidator):
    def validate(self, value):
        if "numerator" not in value:
            raise BadRequest("Missing required field 'numerator'")
        elif "denominator" not in value:
            raise BadRequest("Missing required field 'denominator'")
        try:
            long(value["numerator"])
        except:
            raise BadRequest("The field 'numerator' must be an integer")
        try:
            long(value["denominator"])
        except:
            raise BadRequest("The field 'denominator' must be an integer")
        
        if(value["denominator"] <= 0):
            raise BadRequest("The field 'denominator' must be greater than 0")
        elif(value["numerator"] < 0):
            raise BadRequest("The field 'numerator' cannot be negative")
