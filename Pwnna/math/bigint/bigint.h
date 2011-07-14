#ifndef BIGINT_H_
#define BIGINT_H_

#include <string>
#include <iostream>
using std::ostream;
using std::istream;

class BigInteger{
private:
	string number;
	void setNum(const char * i) { number = i; }
public:
	BigInteger(const char * i);
	BigInteger(int i);
	BigInteger(BigInteger & i);
	BigInteger();
	~BigInteger(){}
	BigInteger & operator+(int i);
	BigInteger & operator+(const BigInteger & i);
	
	BigInteger & operator=(int i);
	BigInteger & operator=(const BigInteger & i);
	
	BigInteger & operator-(int i);
	BigInteger & operator-(const BigInteger & i);
	
	BigInteger & operator*(int i);
	BigInteger & operator*(const BigInteger & i);
	
	BigInteger & operator/(int i);
	BigInteger & operator/(const BigInteger & i);
	
	bool operator<(int i);
	bool operator<(const BigInteger & i);
	
	bool operator>(int i);
	bool operator>(const BigInteger & i);
	
	friend ostream & operator<<(ostream & os, const BigInteger & i);
	friend istream & operator>>(istream & is, BigInteger & i);
}

#endif
