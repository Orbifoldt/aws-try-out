

Run/synthesize:
```shell
npx aws-cdk synth  
```

Diff before deploy
```shell
npx aws-cdk diff MyStackForLearning
```

Deploy
```shell
npx aws-cdk deploy MyStackForLearning
```

Remove everything again
```shell
npx aws-cdk destroy MyStackForLearning
```


## First time: setup support stack
Need to bootstrap the first time you deploy, creates an S3 bucket and a stack "CDKToolkit".
```shell
npx aws-cdk bootstrap aws://ACCOUNT_ID_HERE/eu-north-1
```

