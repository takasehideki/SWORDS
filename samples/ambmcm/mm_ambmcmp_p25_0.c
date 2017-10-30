#include "xtime_l.h"
#define PROJECT "mm_ambmcmp_p25_0"
#define P 32

int matrixmul_soft(int a[P][P], int b[P][P], int c[P][P]){
	int i,j,k;

	for (i = 0; i < P; i++){
		for (j = 0; j < P; j++){
			c[i][j] = 0;
			for (k = 0; k < P; k++){
				c[i][j] += a[i][k] * b[k][j];
			}
		}
	}

	return 0;

}
int matrixmul(int a[P][P], int b[P][P], int c[P][P]){
   int i,j,k;
#pragma HLS ARRAY_PARTITION variable=c dim=2
   for (i = 0; i < P; i++){
		for (j = 0; j < P; j++){
#pragma HLS PIPELINE II=25
           c[i][j] = 0;
			for (k = 0; k < P; k++){
               c[i][j] += a[i][k] * b[k][j];
		    }
       }
   }
   return 0;
}

int main()
{

	XTime tmp1,tmp2,tmp3,tmp4,tmp5,tmp6;

    init_platform();

    //Xil_DCacheDisable();

    printf("Hello! (%s)\n\r",PROJECT);
    int i,j;

    target_timer_initialize();

    srand(target_timer_get_current());

    int a[P][P], b[P][P], c[P][P], d[P][P], e[P][P];

    for (i = 0;i < P;i++){
    	for (j = 0; j < P;j++){

    		a[i][j] = (int)rand() % 256;
    		b[i][j] = (int)rand() % 256;
    	}
    }

    XTime_GetTime(&tmp1);

    matrixmul_interrupt(a,b,c);

    XTime_GetTime(&tmp2);

    matrixmul(a,b,d);

    XTime_GetTime(&tmp3);

    Xil_DCacheEnable();

    XTime_GetTime(&tmp4);

    matrixmul_soft(a,b,e);

    XTime_GetTime(&tmp5);

    for (i = 0;i < P;i++){
        for (j = 0; j < P;j++){
            if (c[i][j] != d[i][j]) {
            	printf("a[%d][%d] = %d\t",i,j,a[i][j]);
            	printf("b[%d][%d] = %d\t",i,j,b[i][j]);
            	printf("c[%d][%d] = %d\t",i,j,c[i][j]);
            	printf("d[%d][%d] = %d\t",i,j,d[i][j]);
            	printf("e[%d][%d] = %d\n",i,j,e[i][j]);
            }
        }
    }


    printf("hard interr time:%d\n",1.0 * (tmp2 - tmp1) / (COUNTS_PER_SECOND/1000000));
    printf("hard poling time:%d\n",1.0 * (tmp3 - tmp2) / (COUNTS_PER_SECOND/1000000));
    printf("soft time:%d\n",1.0 * (tmp5 - tmp4) / (COUNTS_PER_SECOND/1000000));

    printf("(%s)\n\r",PROJECT);

    cleanup_platform();
    return 0;
}
