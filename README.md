# npy-twitter-bot
CLI Python Twitter v2 API bot

## Prepare for work
1. git clone https://github.com/mikebgrep/npy-twitter-bot.git
2. pip install -r requirements.txt
3. Add API Information in auth.py
4. Set you filter preferences in filters.py
5. Start using the bot

## Arguments from  npy-twitter-bot.py

```
usage: npy-twitter-bot.py [-h] [--follow FOLLOW] [--unfollow UNFOLLOW]
                          [--amount AMOUNT] [--username USERNAME]
                          [--hashtag HASHTAG] [--scrape SCRAPE]
                          [--unlike UNLIKE] [--like LIKE]

Twiter Bot arguments commands

options:
  -h, --help           show this help message and exit
  --follow FOLLOW      fusrf - follow followers of an user, fhtg - follow by
                       hastag,
  --unfollow UNFOLLOW  myfollows - unfollow your follows
  --amount AMOUNT      enter amount to interact from 1 - 1000
  --username USERNAME  username of the user you want to interact
  --hashtag HASHTAG    hashtag to interact with
  --scrape SCRAPE      myfollowers, userlikes, usertweets - to scrape your
                       followers and save to database
  --unlike UNLIKE      tweets - unlike liked tweets by your account
  --like LIKE          usrtweet - like tweets by your account
  ```
  
## Usage

```

python3 npy-twitter-bot.py --follow fusrf --amount AMOUNT --username TARGET_USERNAME
## follow fusrf - follow user followers, amount from 1 to 1000, username is the username of the account with followers you will use 


python3 npy-twitter-bot.py --follow fhtg --hashtag TARGET_HASHTAG --amount AMOUNT 
## follow fhtg from - follow from  hashtag, hashtag name of the hashtag, amount from 1 to 500 results


python3 npy-twitter-bot.py --unfollow myfollows --amount 2000
Note: unfollow myfollows - unfollow from your followers, amount number to unfollow from 0 - 2000

python3 npy-twitter-bot.py --unlike tweets --amount AMOUNT 
## Unlike liked tweets from you account x AMOUNT


python3 npy-twitter-bot.py --like usrtweet --username USERNAME --amount AMOUNT 
## This command will like user tweets with username USERNAME and amount AMOUNT


Note: You can use multiple arguments in one command:

python3 npy-twitter-bot.py --follow "fusrf fhtg" --like usrtweet --unlike tweets --username USERNAME --amount AMOUNT --hashtag HASHTAG 

## This command will follow by user followers and hashtag from -username argument value and --hashtag argument value
## will like tweetes from --username argument value and will unlike tweetes you already liked with your profile.
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
