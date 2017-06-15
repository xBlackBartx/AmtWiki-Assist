import os
import pickle
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Post:
    def __init__(self, page_link, page_name, delete_link, history_link, user_link, user_name, talk_link, contribs_link,
                 block_link, rollback_link, text, new_page):
        self.page_link = page_link
        self.page_name = page_name
        self.delete_link = delete_link
        self.history_link = history_link
        self.user_link = user_link
        self.user_name = user_name
        self.talk_link = talk_link
        self.contribs_link = contribs_link
        self.block_link = block_link
        self.rollback_link = rollback_link
        self.text = text
        self.new_page = new_page

    def __str__(self):
        return self.page_name

    def __eq__(self, other):
        return self.page_link == other.page_link


class Web:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.post_list = []

    @staticmethod
    def get_credentials(retry=False):
        if os.path.isfile('config.wki') and not retry:
            with open('config.wki', 'rb') as file:
                username, pw = pickle.load(file)
                save = False

        else:
            username = input('Username: \n')
            pw = input('Password: \n')
            save = input('Save?\n')
            save = save.lower() == 'y'
        return username, pw, save

    def login(self, retry=False):
        username, password, save = self.get_credentials(retry=retry)
        self.driver.get('http://amtwiki.net/amtwiki/index.php?title=Special:UserLogin&returnto=Special%3ARecentChanges')
        # submit credentials
        self.driver.find_element_by_id('wpName1').send_keys(username)
        self.driver.find_element_by_id('wpPassword1').send_keys(password)
        self.driver.find_element_by_id('wpLoginAttempt').click()
        try:
            WebDriverWait(self.driver, 15).until(ec.title_contains('Recent changes - AmtWiki'))
        except TimeoutException:
            if len(self.driver.find_elements_by_class_name('errorbox')) > 0:  # Login failed
                print('LOGIN FAILED')
                self.login(retry=True)
            else:  # Page timed out
                print('Error loading page, timeout')
                self.exit_program()
        # filter patrolled posts
        if save:
            with open('config.wki', 'wb') as file:
                pickle.dump((username, password), file)
        self.driver.get('http://amtwiki.net/amtwiki/index.php?title=Special:RecentChanges&hidepatrolled=1')

    def get_posts(self, rescan=False):
        if rescan:
            self.post_list = []
            self.driver.get('http://amtwiki.net/amtwiki/index.php?title=Special:RecentChanges&hidepatrolled=1')
            try:
                WebDriverWait(self.driver, 15).until(ec.title_contains('Recent changes - AmtWiki'))
            except TimeoutException:
                if len(self.driver.find_elements_by_class_name('errorbox')) > 0:  # Login failed
                    print('LOGIN FAILED')
                    self.login(retry=True)
                else:  # Page timed out
                    print('Error loading page, timeout')
                    self.exit_program()
        post_sets = self.driver.find_elements_by_class_name('special')
        for post_set in post_sets:
            found_posts = post_set.find_elements_by_tag_name('li')
            for post in found_posts:
                newpage = len(post.find_elements_by_class_name('newpage')) > 0
                links = post.find_elements_by_tag_name('a')
                try:
                    text = post.find_element_by_class_name('comment').text
                except NoSuchElementException:
                    text = ''
                index = 0 if newpage else 1
                try:
                    rollback = post.find_element_by_class_name('mw-rollback-link').find_element_by_tag_name(
                        'a').get_attribute('href')
                except NoSuchElementException:
                    rollback = None

                page = links[1 + index].get_attribute('href')
                page_name = page.split('/')[-1]
                delete_link = f'http://amtwiki.net/amtwiki/index.php?title={page_name}&action=delete'
                history_link = f'http://amtwiki.net/amtwiki/index.php?title={page_name}&action=history'
                user_name = links[2 + index].text
                print(f'Processing {page_name} {user_name}')
                self.post_list.append(Post(
                    page_link=page,
                    page_name=page_name,
                    delete_link=delete_link,
                    history_link=history_link,
                    user_link=links[2 + index].get_attribute('href'),
                    user_name=user_name,
                    talk_link=links[3 + index].get_attribute('href'),
                    contribs_link=links[4 + index].get_attribute('href'),
                    block_link=links[5 + index].get_attribute('href'),
                    rollback_link=rollback,
                    text=text,
                    new_page=newpage
                ))

    def block_user(self, post):
        self.driver.get(post.block_link)
        try:
            WebDriverWait(self.driver, 30).until(ec.title_contains('Block user - AmtWiki'))
        except TimeoutException:
            print("Error, block page timed out")
            self.exit_program()
        self.driver.find_element_by_id('mw-input-wpExpiry').send_keys('i')
        self.driver.find_element_by_id('mw-input-wpReason').send_keys('b')
        self.driver.find_element_by_class_name('mw-htmlform-submit').click()
        try:
            WebDriverWait(self.driver, 30).until(ec.title_contains('Block succeeded'))
        except TimeoutException:
            print("Error, block page timed out")
            self.exit_program()

    def delete_page(self, post):
        self.driver.get(post.page_link)
        self.driver.find_element_by_id('ca-delete').click()
        try:
            WebDriverWait(self.driver, 30).until(ec.title_contains('Delete'))
        except TimeoutException:
            print("Error, delete page timed out")
            self.exit_program()
        self.driver.find_element_by_id('wpDeleteReasonList').send_keys('s')
        self.driver.find_element_by_id('wpReason').clear()
        self.driver.find_element_by_id('wpConfirmB').click()
        try:
            WebDriverWait(self.driver, 30).until(ec.title_contains('Action complete'))
        except TimeoutException:
            print("Error, delete page timed out")
            self.exit_program()

    def roll_back_post(self, post):
        self.driver.get(post.rollback_link)
        self.driver.find_element_by_class_name('mw-htmlform-submit').click()
        input('rollback')

    def approve_page(self, post):
        #  TODO Deal with redirects, errors, and allow for manual patrols
        def link_has_gone_stale(ele):
            try:
                # poll the link with an arbitrary call
                ele.find_elements_by_id('globalWrapper')
                return False
            except StaleElementReferenceException:
                return True

        def wait_for(ele, condition_function):
            start_time = time.time()
            while time.time() < start_time + 5:
                if condition_function(ele):
                    return True
                else:
                    time.sleep(0.1)
                raise Exception('Timeout waiting for page load')

        if post.new_page:
            self.driver.get(post.page_link)
            approve = self.driver.find_elements_by_link_text('Mark this page as patrolled')
            if len(approve) > 0:
                self.driver.get(approve[0].get_attribute('href'))
                try:
                    WebDriverWait(self.driver, 30).until(ec.title_contains('Marked as patrolled'))
                except TimeoutException:
                    print("Error patrolling page, timed out")
                    self.exit_program()
        else:
            self.driver.get(post.page_link)
        history = self.driver.find_element_by_id('ca-history')
        history.click()
        try:
            WebDriverWait(self.driver, 30).until(ec.title_contains('Revision history of'))
        except TimeoutException:
            print('Error in retrieving history, page not loaded.')
            self.exit_program()
        try:
            self.driver.find_element_by_class_name('historysubmit').click()
        except NoSuchElementException:
            return
        updates = [update for update in self.post_list if update.page_name == post.page_name]
        print(f'{len(updates)} updates')
        for _ in updates:
            while True:
                try:
                    pl = self.driver.find_element_by_link_text('Mark as patrolled')
                    pl.click()
                except NoSuchElementException:
                    try:
                        prev = self.driver.find_element_by_id('differences-prevlink')
                        prev.click()
                        wait_for(prev, link_has_gone_stale)
                        continue
                    except NoSuchElementException:
                        break
                try:
                    WebDriverWait(self.driver, 30).until(ec.title_contains('Marked as patrolled'))
                    self.driver.back()
                    try:
                        prev = self.driver.find_element_by_id('differences-prevlink')
                        prev.click()
                        wait_for(prev, link_has_gone_stale)
                    except NoSuchElementException:
                        break
                    break
                except TimeoutException:
                    print('Error in Patrolling, page not loaded.')
                    self.exit_program()

    def display(self, post):
        if post.text and not post.new_page:
            print(post.text)
        print(f'User: {post.user_name}')
        self.driver.get(post.page_link)
        num_edits = len([edits for edits in self.post_list if edits.page_name == post.page_name])
        print(f'{num_edits} edit{["","s"][num_edits > 1]}.')
        answer = input('Spammer?')
        return answer

    def process_posts(self):
        posts_to_process = [post for post in self.post_list if post.new_page]
        processed_pages = []
        for post in self.post_list:
            if post not in posts_to_process:
                posts_to_process.append(post)

        for post in posts_to_process:
            if post.page_name not in processed_pages:
                answer = self.display(post)
                processed_pages.append(post.page_name)
                if answer.lower() == 'y':
                    self.delete_page(post)
                    self.block_user(post)
                elif answer.lower() == 'x':
                    self.exit_program()
                elif answer.lower() == 's':
                    continue  # Skip this post
                else:
                    self.approve_page(post)
        self.get_posts(rescan=True)
        if self.post_list:
            self.process_posts()
        else:
            self.exit_program()

    def exit_program(self):
        self.driver.quit()
        exit()

#  TODO GUI
if __name__ == "__main__":
    web = Web()
    web.login()
    web.get_posts()
    if web.post_list:
        web.process_posts()
    web.exit_program()
