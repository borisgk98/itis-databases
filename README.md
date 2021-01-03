# itis-databases
Домашние задания по курсу "Системы управления хранилищами данных", ИТИС, 4 курс

## Задание 2
Пункты 1-3 я выполнял на aws, для остальных заданий я разворачивал собственную инфраструктуру.
#### 1.
Настройка aws
```
aws configure
```
Получение доступных узлов
```
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].{Instance:InstanceId,Subnet:SubnetId,State:State.Name}' \
    --output json
```
#### 2.
Создание инстанса
```
aws opsworks --region us-east-1 create-instance --stack-id 935450cc-61e0-4b03-a3e0-160ac817d2bb --layer-ids 5c8c272a-f2d5-42e3-8245-5bf3927cb65b --hostname myinstance1 --instance-type m1.large --os "Amazon Linux"
```
#### 3.
Проверка связи с помощью команды `ping`

#### 4-5.
Далее для разворачивания cassandra и системы мониторинга я использовал кластер на основе [microk8s](https://microk8s.io/) на базе Ubuntu.
Установка
```
sudo snap install microk8s --classic
```
Включение службы dns, службы [мониторинга prometheus](https://github.com/prometheus-operator/prometheus-operator), [службы для создания балансировщиков нагрузки](https://metallb.universe.tf/usage/), пакетный менаджер helm, дополненние storage (позволяет использовать и создавать ресурсы для хранилища)
```
microk8s enable dns prometheus metallb helm3 storage
```
Для установки cassandra в кластер будем использовать helm и подготовленный helm-chart https://github.com/bitnami/charts/tree/master/bitnami/cassandra
Параметры, которые нам надо поменять для установки:
- dbUser.user = admin (пользователь касандры)
- dbUser.password = cassPass1234 (пароль касандры)
- replicaCount = 3 (количество узлов касандры)
- metrics.enabled = true (включаем метрики)
- metrics.serviceMonitor.namespace = monitoring (пространство имен для системы мониторинга)
- metrics.serviceMonitor.enabled = true (включаем ServiceMonitoring для сервисов касандры)
- service.type = LoadBalancer (тип сервиса - балансировщик награзки)

Устанавливаем cassandra:
```
helm install cassandra --namespace=default --values=hw2/cassandra-helm-values.yaml bitnami/cassandra
```
#### 6.
В качестве сервера для тестирования я буду использовать свой ноутбук (заместо четвертого узла ec2).
#### 7.
Создание таблицы
```
CREATE KEYSPACE test WITH REPLICATION = {
   'class' : 'SimpleStrategy',
   'replication_factor' : 1
  };

CREATE TABLE test.TEST (
    id int primary key,
    name text
);
```
Программа для заполненния: [hw2/generator.py](https://github.com/borisgk98/itis-databases/blob/main/hw2/generator.py)
#### 8.
Для определения количества записей на каждом узле я использовал nodetool
```
kubectl exec -it cassandra-2 -- nodetool cfstats test.test | grep "Write Count"
```
Для создания графика я использовал matplotlib. [Исходный код](https://github.com/borisgk98/itis-databases/blob/main/hw2/histogram.py)
![Разпределение данных по узлам](https://github.com/borisgk98/itis-databases/blob/main/hw2/histogram.png)

## Задание 3
#### 1-2.
В задание 2 мы уже настроили prometheus operator для сбора метрик
#### 3.
Тут нужно настроить графики в графане.
Для соединения с графаной используем следующую команду:
```
kubectl -n monitoring port-forward grafana-7c9bc466d8-lbgr9 3000:3000
```
После настройки графиков ([сам дашборд для кассандры](https://github.com/borisgk98/itis-databases/blob/main/hw3/cassandra-dashboard.json))) получаем следующую картину:
![График](https://github.com/borisgk98/itis-databases/blob/main/hw3/grafana.png)