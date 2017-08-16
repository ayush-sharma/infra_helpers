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
            print('> No Backoff > Retry number: %s' % str(counter))

        counter += 1


def linear_backoff(max_retry: int):
    """ Linear backoff. If things fail, retry with linearly increasing delays. """

    counter = 0
    while counter < max_retry:

        response = do_something()
        if response:

            return True
        else:

            sleepy_time = counter
            print('> Linear Backoff > Retry number: %s, sleeping for %s seconds.' % (str(counter), str(sleepy_time)))
            # sleep(sleepy_time)

        counter += 1


def exponential_backoff(max_retry: int):
    """ Exponential backoff. If things fail, retry with exponentially increasing delays. """

    counter = 0
    while counter < max_retry:

        response = do_something()
        if response:

            return True
        else:

            sleepy_time = counter ** 2
            print('> Exponential Backoff > Retry number: %s, sleeping for %s seconds.' % (str(counter), str(sleepy_time)))
            # sleep(sleepy_time)

        counter += 1


if __name__ == '__main__':
    max_retries = 10
    print('Starting experiments with maximum %s retries.' % str(max_retries))

    no_backoff(max_retry=max_retries)
    linear_backoff(max_retry=max_retries)
    exponential_backoff(max_retry=max_retries)
