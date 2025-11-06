"""
Mathematical utility functions
"""


def add(a: float, b: float) -> float:
    """
    Add two numbers together
    
    Args:
        a (float): First number
        b (float): Second number
        
    Returns:
        float: Sum of a and b
    """
    return a + b


def add_multiple(*numbers: float) -> float:
    """
    Add multiple numbers together
    
    Args:
        *numbers: Variable number of float arguments
        
    Returns:
        float: Sum of all numbers
    """
    return sum(numbers)


if __name__ == "__main__":
    # Example usage
    result1 = add(5, 3)
    print(f"5 + 3 = {result1}")
    
    result2 = add_multiple(1, 2, 3, 4, 5)
    print(f"1 + 2 + 3 + 4 + 5 = {result2}")

# Created-By: GitHub Copilot