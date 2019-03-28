#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkAccessManager>
#include <QJsonObject>
#include <QJsonDocument>
#include <QByteArray>
#include <QMessageBox>
#include <QtNetwork/QNetworkReply>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::onfinish(QNetworkReply *rep)
{
    QByteArray bts = rep->readAll();
    QString str(bts);
    QMessageBox::information(this,"reply",str,"ok");
}

void MainWindow::on_loginButton_clicked()
{
    QUrl serviceUrl = QUrl("192.168.1.69:7777/app/login");
    QNetworkRequest request(serviceUrl);
    QJsonObject logindata;
    logindata.insert("username", ui->usernameEdit->text());
    logindata.insert("raw_password", ui->usernameEdit->text());
    QJsonDocument jsonDoc(logindata);
    QByteArray jsonData = jsonDoc.toJson();
    request.setHeader(QNetworkRequest::ContentTypeHeader,"application/json");
    request.setHeader(QNetworkRequest::ContentLengthHeader,QByteArray::number(jsonData.size()));
    QNetworkAccessManager *networkManager = new QNetworkAccessManager(this);
    connect(networkManager, SIGNAL(finished(QNetworkReply*)), this, SLOT(onfinish(QNetworkReply*)));
    QNetworkReply *reply = networkManager->post(request, jsonData);
    while(!reply->isFinished())
    {
        qApp->processEvents();
    }
}
