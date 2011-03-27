/* example1.c */

#include <stdio.h>
#include <math.h>

#include "emd.h"

float **TypeDistanceMat;
float MaxDistValue;

float dist_staypoint(feature_t *F1, feature_t *F2)
{
    float distance = abs(*F1 - *F2);
    distance = distance / MaxDistValue;
    return distance;
}

float emd_staypoint(signature_t *Signature1, signature_t *Signature2)
{
    return emd(Signature1, Signature2, dist_staypoint, 0, 0);
}



int setMaxDistValue( float maxDistValue){
    MaxDistValue = maxDistValue;
    return 0;
}

int setTypeDistanceMat( int numTypes, float *dists){
    int i, j;

    TypeDistanceMat = malloc( (numTypes+1) * 4);

    for(i=0; i<numTypes;i++){
        TypeDistanceMat[i] = malloc( (numTypes+1) * 4);
        for(j=0; j<numTypes;j++){
            TypeDistanceMat[i][j] = dists[i*numTypes+j];
        }
    }
    return 0;
}

float dist_type(feature_t *F1, feature_t *F2) { 
    return TypeDistanceMat[*F1][*F2]; 
}

float emd_type(signature_t *Signature1, signature_t *Signature2)
{
    return emd(Signature1, Signature2, dist_type, 0, 0);
}

void test1(){
    feature_t f1[5] = { 0, 20, 40, 60, 80 };
    feature_t f2[5] = { 0, 20, 40, 60, 80 };

    float w1[5] = { 0.1, 0.2, 0.2, 0.2, 0.3 };
    float w2[5] = { 0.2, 0.2, 0.2, 0.2, 0.2 };

    signature_t s1 = { 5, f1, w1};
    signature_t s2 = { 5, f2, w2};

    float e;
    e = emd_staypoint(&s1, &s2);
    printf("emd_staypoint =%f\n", e);

    return;
}

void test2(){
    feature_t f1[3] = { 0, 1, 2 };
    feature_t f2[3] = { 0, 1, 2 };

    float w1[3] = { 0.3, 0.4, 0.3 };
    float w2[3] = { 0.3, 0.4, 0.3 };

    signature_t s1 = { 3, f1, w1};
    signature_t s2 = { 3, f2, w2};

    float dists[9] = {0,5,2,4,0,8,1,1,0};

    setTypeDistanceMat( 3, dists);

    float e;
    e = emd_type(&s1, &s2);
    printf("emd_type =%f\n", e);
}



void main()
{
    //test1();
    test2();

}

