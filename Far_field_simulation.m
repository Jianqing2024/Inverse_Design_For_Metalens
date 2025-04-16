function [U532,U800]=Far_field_simulation(array)
dbFile = 'structures.db';
conn = sqlite(dbFile, 'readonly');

[sizeX,sizeY]=size(array);

Phi532=zeros(sizeX,sizeY);
Phi800=zeros(sizeX,sizeY);
for i=1:sizeX
    for j=1:sizeY
        ID=array(i,j);
        query=sprintf('SELECT %s, %s FROM structures WHERE id = %d', "angleIn532", "angleIn800", ID);
        data=fetch(conn,query);
        data=table2array(data);
        Phi532(i,j)=data(1);
        Phi800(i,j)=data(2);
    end
end

query=sprintf('SELECT %s FROM structures WHERE id = %d', "P", array(1,1));
single=table2array(fetch(conn,query));
x=generate_symmetric_vector(sizeX,single);

[X0,Y0]=meshgrid(x,x);

close(conn);
E532=exp(1i*Phi532);
E800=exp(1i*Phi800);

z=linspace(0.5e-3,5e-3,100);

U532=RSaxis(E532,0.532e-6,X0,Y0,z);
U800=RSaxis(E800,0.800e-6,X0,Y0,z);

function vec = generate_symmetric_vector(N, step)
half = N / 2;
vec = ((-half : half - 1) + 0.5) * step;
end
end