# itis-databases
Домашние задания по курсу "Системы управления хранилищами данных", ИТИС, 4 курс

## Задание 2
Пункты 1-3 я выполнял на aws, для остальных заданий я разворачивал собственную инфраструктуру.
1. Настройка aws
```
aws configure
```
Получение доступных узлов
```
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].{Instance:InstanceId,Subnet:SubnetId,State:State.Name}' \
    --output json
```
2. Создание инстанса
```
aws opsworks --region us-east-1 create-instance --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --layer-ids 5c8c272a-f2d5-42e3-8245-5bf3927cb65b --hostname myinstance1 --instance-type m1.large --os "Amazon Linux"
```
3. Проверка связи с помощью команды `ping`
