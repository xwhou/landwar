#include "common.h"


char* itoa(int num,char*str,int radix)
{
  /*索引表*/
  char index[]="0123456789ABCDEF";
  unsigned unum;/*中间变量*/
  int i=0;
  int j,k;
  /*确定unum的值*/
  if(radix == 10 && num<0)/*十进制负数*/
  {
    unum=(unsigned)-num;
    str[i++]='-';
  }
  else unum=(unsigned)num;/*其他情况*/
  /*转换*/
  do{
  str[i++]=index[unum%(unsigned)radix];
  unum/=radix;
  }while(unum);
  str[i]='\0';
  /*逆序*/
  if(str[0]=='-')k=1;/*十进制负数*/
  else k=0;
  char temp;
  for(j=k;j<=(i-1)/2;j++)
  {
  temp=str[j];
  str[j]=str[i-1+k-j];
  str[i-1+k-j]=temp;
  }
  return str;
}

bool cvtIntLocTo4StrOffLoc(const int int_loc, char *str_4_offloc, const int arr_char_len)
{
  char * tmpstr = malloc(sizeof(char) * arr_char_len);
  memset(tmpstr, '0', sizeof(char) * arr_char_len);
  memcpy(str_4_offloc, tmpstr, sizeof(char) * arr_char_len);
  str_4_offloc[arr_char_len-1]='\0';

  itoa(int_loc, tmpstr,10);
  int str_len = strlen(tmpstr);

 /* if (str_len > 4)
  {
    printf("error in cvtIntLocTo4StrOffLoc() : len > 4 \n");
    return false;
  }
*/

  memcpy(str_4_offloc + (arr_char_len-2) - (str_len-1), tmpstr, str_len);

  free(tmpstr);
  return true;
}


void cvtChars6locToOffsetIntLoc(const char * chars_6_loc, int * p_row, int *p_col)
{
  assert(strlen(chars_6_loc) == 6);
  char chars_f_2[]={'\0','\0','\0'};
  memcpy(chars_f_2, chars_6_loc, sizeof(char)*2);
  int int_first_2 = atoi(chars_f_2);
  char chars_l_3[]={'\0','\0','\0','\0'};
  memcpy(chars_l_3, chars_6_loc + 3, sizeof(char)*3);
  int int_last_3 = atoi(chars_l_3);
  if (int_last_3 % 2 == 1)
  {
    *p_row = int_first_2 * 2 + 1;
    *p_col = (int_last_3 - 1) / 2;
  }
  else
  {
    *p_row = int_first_2 * 2 ;
    *p_col = int_last_3 / 2 ;
  }
  return;
}

int cvtOffsetIntLocToInt6(const int row, const int col)
{
 int tmpfirst,tmplast;
 if (row % 2 == 1)
 {
    tmpfirst = (row - 1) / 2;
    tmplast = col * 2 + 1;
 }
 else
 {
    tmpfirst = row / 2 ;
    tmplast = col * 2;
 }
 
   if (tmpfirst < 0 || tmplast < 0){
    printf("row = %d, col = %d\n", row, col);
  }

  assert(tmplast >= 0 && tmpfirst >= 0);
 return tmpfirst * 10000 + tmplast;
}


int cvtInt6loc2Int4loc(const int int6loc)
{
  //  printf("int6loc = %d\n", int6loc);
  char chars_6loc[7] = {'\0'};
  cvtIntLocTo4StrOffLoc(int6loc, chars_6loc, 7);
  int row = 0; int col = 0;
  cvtChars6locToOffsetIntLoc(chars_6loc, &row, &col);
  if(!(col >=0 && col < 100))
    printf("int6loc = %d ==>  row = %d, col = %d\n", int6loc , row, col);
  assert(row >=0 && row < 100 );
  assert(col >=0 && col < 100 );
  return row * 100 + col;

}


bool findmaxfloat(const float *p_arr, const int len, float * p_maxvalue, int *p_maxindex)
{
  if (len <= 0){
    // printf("error in findmaxfloat(). len = %d\n", len);
    return false;
  }

  float maxvalue = p_arr[0];
  int maxindex = 0;
  for(int i = 1 ; i < len; i++){
    if(p_arr[i]>maxvalue)  {
      maxvalue = p_arr[i];
      maxindex = i;
    }
  }
  *p_maxindex = maxindex;
  *p_maxvalue = maxvalue;
  return true;
}

void getComLocFrom2Int6Locs(const int int6loca , const int int6locb, const int len_comchar, char* p_comchar)
{
  char char_7loca[7] = {'\0'};
  cvtIntLocTo4StrOffLoc(int6loca, char_7loca, 7);
  char char_7locb[7] = {'\0'};
  cvtIntLocTo4StrOffLoc(int6locb, char_7locb, 7);
  assert(len_comchar == 13);
  memcpy(p_comchar, char_7loca, sizeof(char) * 6);
  memcpy(p_comchar + 6, char_7locb, sizeof(char) * 6);
  return ;
}
