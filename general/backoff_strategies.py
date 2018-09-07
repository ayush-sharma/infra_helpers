from time import sleep


def do_something():
    """ This is our testing function. As long as this function returns false, our retry functions below will keep
    retrying. """
    
    return False


def no_backoff(max_retry: int):
    """ No backoff. If things fail, retry immediately. """
    
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            print('> No Backoff > Retry number: %s' % counter)
            pass
        
        counter += 1


def constant_backoff(max_retry: int):
    """ Constant backoff. If things fail, retry after a fixed amount of delay. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = 1
            print('> Constant Backoff > Retry number: %s, sleeping for %s seconds.' % (counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Constant Backoff > Total delay: %s seconds.' % total_delay)


def linear_backoff(max_retry: int):
    """ Linear backoff. If things fail, retry with linearly increasing delays. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = counter
            print('> Linear Backoff > Retry number: %s, sleeping for %s seconds.' % (counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Linear Backoff > Total delay: %s seconds.' % total_delay)


def get_fib(num: int):
    """ Get sum of Fibonacci numbers up to given number. """
    
    if num <= 1:
        
        return num
    else:
        return get_fib(num - 1) + get_fib(num - 2)


def fibonacci_backoff(max_retry: int):
    """ Fibonacci backoff. If things fail, retry with delays increasing by fibonacci numbers. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = get_fib(counter)
            print(
                    '> Fibonacci Backoff > Retry number: %s, sleeping for %s seconds.' % (
                        counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Fibonacci Backoff > Total delay: %s seconds.' % total_delay)


def exponential_backoff(max_retry: int):
    """ Exponential backoff. If things fail, retry with exponentially increasing delays. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = 2 ** counter
            print(
                    '> Exponential Backoff > Retry number: %s, sleeping for %s seconds.' % (
                        counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Exponential Backoff > Total delay: %s seconds.' % total_delay)


def quadratic_backoff(max_retry: int):
    """ Quadratic backoff. If things fail, retry with polynomially increasing delays. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = counter ** 2
            print(
                    '> Quadratic Backoff > Retry number: %s, sleeping for %s seconds.' % (
                        counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Quadratic Backoff > Total delay: %s seconds.' % total_delay)


def polynomial_backoff(max_retry: int):
    """ Polynomial backoff. If things fail, retry with polynomially increasing delays. """
    
    total_delay = 0
    counter = 0
    while counter < max_retry:
        
        response = do_something()
        if response:
            
            return True
        else:
            
            sleepy_time = counter ** 3
            print(
                    '> Polynomial Backoff > Retry number: %s, sleeping for %s seconds.' % (
                        counter, sleepy_time))
            total_delay += sleepy_time
            sleep(sleepy_time)
        
        counter += 1
    
    print('> Polynomial Backoff > Total delay: %s seconds.' % total_delay)


if __name__ == '__main__':
    
    max_retries = 3
    print('Starting tests with maximum %s retries.' % str(max_retries))
    
    no_backoff(max_retry=max_retries)
    constant_backoff(max_retry=max_retries)
    linear_backoff(max_retry=max_retries)
    fibonacci_backoff(max_retry=max_retries)
    quadratic_backoff(max_retry=max_retries)
    exponential_backoff(max_retry=max_retries)
    polynomial_backoff(max_retry=max_retries)
